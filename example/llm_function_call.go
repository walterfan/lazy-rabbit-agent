package main

import (
	"bytes"
	"encoding/json"
	"flag"
	"fmt"
	"io"
	"net/http"
	"os"
	"strings"
)

// CityCodes maps city names to their codes
var CityCodes = map[string]string{
	"合肥市":   "340100",
	"合肥":    "340100",
	"HEFEI": "340100",
	"芜湖市":   "340200",
	"芜湖":    "340200",
	"WUHU":  "340200",
}

// WeatherResponse represents the response from the weather API
type WeatherResponse struct {
	Status   string `json:"status"`
	Count    string `json:"count"`
	Info     string `json:"info"`
	Infocode string `json:"infocode"`
	Lives    []struct {
		Province         string `json:"province"`
		City             string `json:"city"`
		Adcode           string `json:"adcode"`
		Weather          string `json:"weather"`
		Temperature      string `json:"temperature"`
		WindDirection    string `json:"winddirection"`
		WindPower        string `json:"windpower"`
		Humidity         string `json:"humidity"`
		ReportTime       string `json:"reporttime"`
		TemperatureFloat string `json:"temperature_float"`
		HumidityFloat    string `json:"humidity_float"`
	} `json:"lives"`
}

// OpenAIRequest represents the request to OpenAI API
type OpenAIRequest struct {
	Model      string    `json:"model"`
	Messages   []Message `json:"messages"`
	Tools      []Tool    `json:"tools"`
	ToolChoice string    `json:"tool_choice"`
}

// OpenAIResponse represents the response from OpenAI API
type OpenAIResponse struct {
	Choices []struct {
		Message Message `json:"message"`
	} `json:"choices"`
}

// Message represents a message in the conversation
type Message struct {
	Role       string     `json:"role"`
	Content    string     `json:"content"`
	ToolCalls  []ToolCall `json:"tool_calls,omitempty"`
	ToolCallID string     `json:"tool_call_id,omitempty"`
}

// Tool represents a tool definition
type Tool struct {
	Type     string   `json:"type"`
	Function Function `json:"function"`
}

// Function represents a function definition
type Function struct {
	Name        string                 `json:"name"`
	Description string                 `json:"description"`
	Parameters  map[string]interface{} `json:"parameters"`
	Arguments   string                 `json:"arguments,omitempty"`
}

// ToolCall represents a tool call from the model
type ToolCall struct {
	ID       string   `json:"id"`
	Type     string   `json:"type"`
	Function Function `json:"function"`
}

// getCityCode returns the city code for a given city name
func getCityCode(cityName string) string {
	cityName = strings.ToUpper(strings.TrimSpace(cityName))
	if code, exists := CityCodes[cityName]; exists {
		return code
	}
	return "340100" // Default to Hefei
}

// sendMessages sends messages to the OpenAI API and returns the response
func sendMessages(messages []Message, apiKey, baseURL, model string) (*Message, error) {
	request := OpenAIRequest{
		Model:      model,
		Messages:   messages,
		Tools:      getTools(),
		ToolChoice: "auto",
	}

	jsonData, err := json.Marshal(request)
	if err != nil {
		return nil, fmt.Errorf("failed to marshal request: %v", err)
	}

	req, err := http.NewRequest("POST", baseURL+"/chat/completions", bytes.NewBuffer(jsonData))
	if err != nil {
		return nil, fmt.Errorf("failed to create request: %v", err)
	}

	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("Authorization", "Bearer "+apiKey)

	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		return nil, fmt.Errorf("failed to send request: %v", err)
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("failed to read response: %v", err)
	}

	var openAIResp OpenAIResponse
	if err := json.Unmarshal(body, &openAIResp); err != nil {
		return nil, fmt.Errorf("failed to unmarshal response: %v", err)
	}

	if len(openAIResp.Choices) == 0 {
		return nil, fmt.Errorf("no choices in response")
	}

	return &openAIResp.Choices[0].Message, nil
}

// getTools returns the available tools
func getTools() []Tool {
	return []Tool{
		{
			Type: "function",
			Function: Function{
				Name:        "get_weather",
				Description: "Get weather of a location. User must supply a location first.",
				Parameters: map[string]interface{}{
					"type": "object",
					"properties": map[string]interface{}{
						"location": map[string]interface{}{
							"type":        "string",
							"description": "The city and state, e.g., 合肥市",
						},
					},
					"required": []string{"location"},
				},
			},
		},
	}
}

// getWeather fetches weather information from the weather API
func getWeather(cityCode, apiKey string) (*WeatherResponse, error) {
	url := "https://restapi.amap.com/v3/weather/weatherInfo"

	req, err := http.NewRequest("GET", url, nil)
	if err != nil {
		return nil, fmt.Errorf("failed to create request: %v", err)
	}

	q := req.URL.Query()
	q.Add("city", cityCode)
	q.Add("key", apiKey)
	req.URL.RawQuery = q.Encode()

	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		return nil, fmt.Errorf("failed to send request: %v", err)
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("failed to read response: %v", err)
	}

	var weatherResp WeatherResponse
	if err := json.Unmarshal(body, &weatherResp); err != nil {
		return nil, fmt.Errorf("failed to unmarshal response: %v", err)
	}

	return &weatherResp, nil
}

func main() {
	// Parse command line arguments
	var city string
	flag.StringVar(&city, "city", "Hefei", "City name to get weather for")
	flag.Parse()

	// Load environment variables
	apiKey := os.Getenv("LLM_API_KEY")
	baseURL := os.Getenv("LLM_BASE_URL")
	model := os.Getenv("LLM_MODEL")
	lbsAPIKey := os.Getenv("LBS_API_KEY")

	// Check required environment variables
	if apiKey == "" {
		fmt.Println("Error: LLM_API_KEY environment variable is required")
		os.Exit(1)
	}
	if baseURL == "" {
		fmt.Println("Error: LLM_BASE_URL environment variable is required")
		os.Exit(1)
	}
	if model == "" {
		fmt.Println("Error: LLM_MODEL environment variable is required")
		os.Exit(1)
	}
	if lbsAPIKey == "" {
		fmt.Println("Error: LBS_API_KEY environment variable is required")
		os.Exit(1)
	}

	// Initial user message
	messages := []Message{
		{
			Role:    "user",
			Content: fmt.Sprintf("How's the weather in %s?", city),
		},
	}

	fmt.Printf("User> %s\n", messages[0].Content)

	// First call: Model decides to use a tool
	message, err := sendMessages(messages, apiKey, baseURL, model)
	if err != nil {
		fmt.Printf("Error sending messages: %v\n", err)
		os.Exit(1)
	}
	messages = append(messages, *message)

	// Check if a tool was called
	if len(message.ToolCalls) > 0 {
		toolCall := message.ToolCalls[0]
		fmt.Printf("Model> %s(%s)\n", toolCall.Function.Name, toolCall.Function.Arguments)

		// Get weather information
		weatherResp, err := getWeather(getCityCode(city), lbsAPIKey)
		if err != nil {
			fmt.Printf("Error getting weather: %v\n", err)
			os.Exit(1)
		}

		if len(weatherResp.Lives) == 0 {
			fmt.Println("Error: No weather data received")
			os.Exit(1)
		}

		todayWeather := weatherResp.Lives[0]
		toolResponse := fmt.Sprintf("%s is %s, %s°C, at %s",
			todayWeather.City,
			todayWeather.Weather,
			todayWeather.Temperature,
			todayWeather.ReportTime)

		// Add tool response to messages
		messages = append(messages, Message{
			Role:       "tool",
			ToolCallID: toolCall.ID,
			Content:    toolResponse,
		})

		// Final call: Model generates natural language answer
		finalMessage, err := sendMessages(messages, apiKey, baseURL, model)
		if err != nil {
			fmt.Printf("Error sending final message: %v\n", err)
			os.Exit(1)
		}

		fmt.Printf("Model> %s\n", finalMessage.Content)
	} else {
		// No tool called; model provided a direct answer
		fmt.Printf("Model> %s\n", message.Content)
	}
}
