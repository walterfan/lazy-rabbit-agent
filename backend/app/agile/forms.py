from wtforms import Form, SelectField, StringField, TextAreaField, SubmitField

class AgileForm(Form):
    command = SelectField('Command', choices=[
        ('compose', '撰写'),
        ('translate', '翻译'),
        ('summarize', '总结'),
        ('analyze', '分析'),
        ('extract', '提取'),
        ('outline', '提纲'),
        ('mindmap', '思维导图')])

    model = SelectField('Model', choices=[
        ('01-ai/Yi-1.5-9B-Chat-16K', 'Yi-1.5-9B-Chat-16K'),
        ('Qwen/Qwen2.5-7B-Instruct', 'Qwen2.5-7B-Instruct'),
        ('Qwen/Qwen2.5-Coder-7B-Instruct','Qwen2.5-Coder-7B-Instruct'),
        ('THUDM/glm-4-9b-chat', 'glm-4-9b-chat'),
        ('google/gemma-2-9b-it', 'gemma-2-9b-it'),
        ('deepseek-ai/DeepSeek-V2.5', 'DeepSeek-V2.5'),
        ('Qwen/Qwen2.5-32B-Instruct', 'Qwen2.5-32B-Instruct'),
        ('meta-llama/Meta-Llama-3.1-8B-Instruct','Meta-Llama-3.1-8B-Instruct'),
        ('black-forest-labs/FLUX.1-schnell','FLUX.1-schnell')
        ])

    template = SelectField('Template', choices=[
        ('unspecified', 'Unspecified'),
        ('feature', 'Feature'),
        ('story', 'User Story'),
        ('bug', 'Bug'),
        ('sprint_plan', 'Sprint Plan Meeting'),
        ('sprint_retrospective', 'Sprint Retrospective Meeting'),
        ('sprint_review', 'Sprint Review Meeting')])
    prompts = TextAreaField('Prompts', render_kw={'placeholder': 'system_prompt=value1\nuser_prompt=value2'})
    parameters = TextAreaField('Parameters', render_kw={'placeholder': 'text=value1\nurl=value2'})
    invitation = StringField('Invitation')
    input = TextAreaField('Input')
    output = TextAreaField('Output')
    submit = SubmitField('Submit')