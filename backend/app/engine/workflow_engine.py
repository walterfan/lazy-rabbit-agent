import asyncio
import json
import argparse
import sys
from typing import Dict, List, Any, Optional, Callable, Union


class WorkflowEngine:
    def __init__(self):
        """Initialize the workflow engine"""
        self.workflows = {}
        self.current_states = {}
        self.context = {}
        self.callbacks = {}  # Used to store callback functions for each state
        self.event_queue = asyncio.Queue()
        self.running = False
    
    def parse_workflow(self, workflow_str):
        """
        Parse the workflow definition string
        
        Args:
            workflow_str: A string like "start->a;a->b;b->c:condition1;b->d:condition2;c->end;d->end;"
            
        Returns:
            Parsed workflow dictionary
        """
        workflow = {}
        steps = workflow_str.strip(';').split(';')
        
        for step in steps:
            if '->' not in step:
                continue
                
            transition_part = step.split('->')
            source = transition_part[0]
            
            # Handle target and condition
            target_condition = transition_part[1].split(':', 1)
            target = target_condition[0]
            condition = target_condition[1] if len(target_condition) > 1 else None
            
            # Add to workflow
            if source not in workflow:
                workflow[source] = []
            
            workflow[source].append({
                'target': target,
                'condition': condition
            })
        
        return workflow
    
    def load_workflow(self, workflow_id, workflow_str):
        """
        Load a workflow
        
        Args:
            workflow_id: Unique identifier for the workflow
            workflow_str: Workflow definition string
        """
        self.workflows[workflow_id] = self.parse_workflow(workflow_str)
        self.current_states[workflow_id] = 'start'
        self.context[workflow_id] = {}
        self.callbacks[workflow_id] = {}
        print(f"Workflow '{workflow_id}' loaded, starting at 'start' state")
    
    def register_callback(self, workflow_id, state, callback):
        """
        Register a callback function for a specific state in a specific workflow
        
        Args:
            workflow_id: Workflow ID
            state: State name
            callback: Callback function, takes context as an argument
        """
        if workflow_id not in self.callbacks:
            self.callbacks[workflow_id] = {}
        self.callbacks[workflow_id][state] = callback
    
    async def process_event(self, workflow_id, event):
        """
        Process an event
        
        Args:
            workflow_id: Workflow ID
            event: Event to be processed
            
        Returns:
            List of states visited during processing
        """
        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        states_visited = []
        current_state = self.current_states[workflow_id]
        workflow = self.workflows[workflow_id]
        ctx = self.context[workflow_id]
        
        # Update context
        if isinstance(event, dict):
            ctx.update(event)
        else:
            ctx['event'] = event
        
        print(f"Processing event in workflow '{workflow_id}', current state: '{current_state}'")
        states_visited.append(current_state)
        
        # Execute callback function for the current state
        await self._execute_callback(workflow_id, current_state, ctx)
        
        # If already at the end state, return immediately
        if current_state == 'end':
            return states_visited
        
        # State transition loop, until no more transitions or end state is reached
        while current_state in workflow:
            transitions = workflow[current_state]
            next_state = None
            
            for transition in transitions:
                target = transition['target']
                condition = transition['condition']
                
                # If there is no condition or the condition is met, transition to the target state
                if condition is None or self._evaluate_condition(condition, ctx):
                    next_state = target
                    break
            
            if next_state is None:
                # No available transitions, current state is the final state
                break
                
            # Update current state and execute callback
            current_state = next_state
            self.current_states[workflow_id] = current_state
            
            print(f"Transitioned to state: '{current_state}'")
            states_visited.append(current_state)
            
            # Execute callback function for the new state
            await self._execute_callback(workflow_id, current_state, ctx)
            
            # If end state is reached, stop transitioning
            if current_state == 'end':
                break
        
        return states_visited
    
    async def _execute_callback(self, workflow_id, state, context):
        """Execute the callback function associated with the state"""
        if workflow_id in self.callbacks and state in self.callbacks[workflow_id]:
            callback = self.callbacks[workflow_id][state]
            if asyncio.iscoroutinefunction(callback):
                await callback(context)
            else:
                callback(context)
    
    def _evaluate_condition(self, condition, context):
        """
        Evaluate the condition
        
        Args:
            condition: Condition expression
            context: Context variables
            
        Returns:
            Result of the condition evaluation (boolean)
        """
        try:
            # Create a safe execution environment, only allowing access to variables in context
            result = eval(condition, {"__builtins__": {}}, context)
            return bool(result)
        except Exception as e:
            print(f"Error evaluating condition '{condition}': {e}")
            return False
    
    def get_current_state(self, workflow_id):
        """Get the current state of the workflow"""
        if workflow_id not in self.current_states:
            raise ValueError(f"Workflow {workflow_id} not found")
        return self.current_states[workflow_id]
    
    def reset_workflow(self, workflow_id):
        """Reset the workflow to the initial state"""
        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow {workflow_id} not found")
        self.current_states[workflow_id] = 'start'
        self.context[workflow_id] = {}
        print(f"Workflow '{workflow_id}' reset to 'start' state")
    
    async def add_event(self, workflow_id, event):
        """
        Add an event to the queue
        
        Args:
            workflow_id: Workflow ID
            event: Event data
        """
        await self.event_queue.put({
            'workflow_id': workflow_id,
            'event': event
        })
    
    async def start_event_loop(self):
        """Start the event loop to process events in the queue"""
        self.running = True
        print("Event loop started. Waiting for events...")
        
        while self.running:
            try:
                event_data = await self.event_queue.get()
                workflow_id = event_data['workflow_id']
                event = event_data['event']
                
                await self.process_event(workflow_id, event)
                self.event_queue.task_done()
            except Exception as e:
                print(f"Error processing event: {e}")
    
    def stop_event_loop(self):
        """Stop the event loop"""
        self.running = False
        print("Event loop stopped")

    async def start_cli(self):
        """Start the command line interface to receive events"""
        print("CLI interface started. Type 'help' for available commands.")
        
        while self.running:
            try:
                cmd = await asyncio.get_event_loop().run_in_executor(
                    None, lambda: input("\nEnter command: ")
                )
                
                if cmd.lower() == 'exit':
                    self.stop_event_loop()
                    break
                    
                elif cmd.lower() == 'help':
                    print("\nAvailable commands:")
                    print("  event <workflow_id> <json_data> - Send event to workflow")
                    print("  status <workflow_id>            - Get current state of workflow")
                    print("  reset <workflow_id>             - Reset workflow to start state")
                    print("  list                            - List all loaded workflows")
                    print("  exit                            - Exit the program")
                    
                elif cmd.lower() == 'list':
                    if not self.workflows:
                        print("No workflows loaded")
                    else:
                        print("\nLoaded workflows:")
                        for wf_id in self.workflows:
                            print(f"  {wf_id} - Current state: {self.current_states[wf_id]}")
                
                elif cmd.startswith('status '):
                    parts = cmd.split(' ', 1)
                    if len(parts) != 2:
                        print("Invalid command format. Use: status <workflow_id>")
                        continue
                        
                    wf_id = parts[1].strip()
                    if wf_id not in self.workflows:
                        print(f"Workflow '{wf_id}' not found")
                        continue
                        
                    state = self.get_current_state(wf_id)
                    print(f"Current state of workflow '{wf_id}': {state}")
                    
                elif cmd.startswith('reset '):
                    parts = cmd.split(' ', 1)
                    if len(parts) != 2:
                        print("Invalid command format. Use: reset <workflow_id>")
                        continue
                        
                    wf_id = parts[1].strip()
                    if wf_id not in self.workflows:
                        print(f"Workflow '{wf_id}' not found")
                        continue
                        
                    self.reset_workflow(wf_id)
                    
                elif cmd.startswith('event '):
                    parts = cmd.split(' ', 2)
                    if len(parts) != 3:
                        print("Invalid command format. Use: event <workflow_id> <json_data>")
                        continue
                        
                    wf_id = parts[1].strip()
                    if wf_id not in self.workflows:
                        print(f"Workflow '{wf_id}' not found")
                        continue
                        
                    try:
                        event_data = json.loads(parts[2])
                        await self.add_event(wf_id, event_data)
                        print(f"Event sent to workflow '{wf_id}'")
                    except json.JSONDecodeError:
                        print("Invalid JSON format for event data")
                
                else:
                    print("Unknown command. Type 'help' for available commands.")
                    
            except Exception as e:
                print(f"Error processing command: {e}")


async def main():
    parser = argparse.ArgumentParser(description='Workflow Engine')
    parser.add_argument('workflow_file', nargs='?', help='Workflow definition file')
    args = parser.parse_args()
    
    engine = WorkflowEngine()
    
    # Define example callback functions
    async def on_validate_input(context):
        print(f"Validating input: {context}")
        # Simulate some asynchronous operations
        await asyncio.sleep(0.5)
        # Set validation result based on input
        if 'input' in context and context['input'].strip():
            context['input_valid'] = True
            print("Input validation successful")
        else:
            context['input_valid'] = False
            print("Input validation failed - empty input")
    
    def on_process(context):
        print(f"Processing data: {context}")
        # Add processing logic here
    
    def on_notify(context):
        print(f"Sending notification for: {context}")
        # Add notification logic here
    
    def on_error(context):
        print(f"Handling error: {context}")
        # Add error handling logic here
    
    def on_end(context):
        print(f"Workflow completed with context: {context}")
    
    # Define example workflow
    sample_workflow = "start->validate_input;validate_input->process:input_valid==True;validate_input->error:input_valid==False;process->notify;notify->end;error->end;"
    
    # Load workflow
    if args.workflow_file:
        try:
            with open(args.workflow_file, 'r') as f:
                workflow_str = f.read()
            engine.load_workflow("file_workflow", workflow_str)
        except Exception as e:
            print(f"Error loading workflow file: {e}")
            return
    else:
        # Use example workflow
        engine.load_workflow("sample", sample_workflow)
        
        # Register state callbacks
        engine.register_callback("sample", "validate_input", on_validate_input)
        engine.register_callback("sample", "process", on_process)
        engine.register_callback("sample", "notify", on_notify)
        engine.register_callback("sample", "error", on_error)
        engine.register_callback("sample", "end", on_end)
    
    # Start event loop
    event_loop_task = asyncio.create_task(engine.start_event_loop())
    
    # Start CLI
    cli_task = asyncio.create_task(engine.start_cli())
    
    # Wait for tasks to complete
    await asyncio.gather(event_loop_task, cli_task)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nProgram terminated by user")
    except Exception as e:
        print(f"Unexpected error: {e}")