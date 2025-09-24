# Тестовое задаения для компании Manaraga.ai 

## Запуск проекта для разработки: 
1. Создать файл .env по подобию ".env.example"
2. `docker-compose -f docker-compose.dev.yml up`

## Деплой на продакшен (TODO)
`docker-compose -f docker-compose.prod.yml up`

## Оригинальное ТЗ: 
Project - Flights by Country
We’re diving into the world of Google Flights again and want to create an exciting tool to explore the countries that flights arrive from for a specific airport. So an example: We look at London Heathrow airport, flights may arrive from France, Germany, UK itself, and other countries. Users should be able to select one of six airports and ask flight-related questions, with the app providing relevant answers.

Requirements:
User Interface - Create a form with the following elements (see example above):
A dropdown menu to select one of the six airports: DXB, LHR, CDG, SIN, HKG, AMS.
A text input field for the user to type their question.
Get data from the Airport Schedule API from FlightAPI.io (https://www.flightapi.io/). You can sign up for a free API key.
LLM Integration - Query an LLM to interpret the user's question and generate an appropriate answer using the dataset.
Output - Display the generated answer to the user.
Scope and Limitations
Scope of Questions: The app will only handle questions about a single airport at a time. For example:
For SIN: “How many flights arrived from Germany?”
For LHR: “Which cities in the US does BA fly to?”
Questions can reference any data included in the dataset but will always be specific to one airport.
You have full freedom to choose which LLM provider, model and way of implementation best suits you.
Submission Instructions:
Share the source code (publicly) via a GitHub repository
Host the tool on a service of your choice (e.g., Vercel, Render.com, GitHub Pages, etc.) so it is publicly accessible.
Provide a public link to the hosted tool.
