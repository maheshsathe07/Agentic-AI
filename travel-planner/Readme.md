## Workflow for Travel Planner agent:

                        ┌──────────────────────┐
                        │ User types a query   │
                        └──────────┬───────────┘
                                   │
                     ┌─────────────▼───────────────┐
                     │ Is LLM available?            │
                     └─────────────┬───────────────┘
                                   │Yes
                                   ▼
                       ┌───────────────────────────────┐
                       │ LLM decides: action + input    │
                       │ (weather/currency/attractions) │
                       └─────────────┬─────────────────┘
                                     │No valid action
                                     ▼
                      ┌─────────────────────────────────┐
                      │ Apply regex heuristics          │
                      └─────────────┬───────────────────┘
                                    ▼
                 ┌────────────────────────────────────┐
                 │ Execute the chosen tool            │
                 ├────────────────────────────────────┤
                 │ get_real_weather(city)             │
                 │ convert_currency("100 USD EUR")    │
                 │ search_wikipedia_attractions(city) │
                 └────────────────────────────────────┘
