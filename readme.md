# For Value Messenger Bot

For Value is a chatbot on facebook which quickly grabs card prices.

## Usage
Query format: [quantity] [!foil] [!setCode] CardName
- Quantity (optional): How many of that card you would like. Simply multiplies the card price by this number.
- Foil (optional): Finds the foil version of a card instead of the regular version.
- SetCode (optional): Eg. KTK, RTR, M10, MMA. The edition of the card you would like to search for.
- CurrencyCode (optional): Eg. AUD, USD, JPY. The bot will convert the price into the chosen currency.
- CardName (required): The name of the card being searched for.

## Examples
- `cancel` -> `Cancel - 10th Edition (C): AUD 0.36`
- `!foil cancel` -> `FOIL Cancel - 10th Edition (C): AUD 0.44`
- `!ktk cancel` -> `Cancel - Khans of Tarkir (C): AUD 0.31`
- `4 cancel` -> `4 Cancel - 10th Edition (C): AUD 1.45`







