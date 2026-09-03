The stock data is inputted through portfolio.csv. For a given stock (recognised by its Yahoo Finance ticker), the dates of purchasing shares, the amount of shares and the dollar amount invested is tracked. Based on
this information, the total portfolio value is tracked from a starting date. Initially, I was attempting to make the tracker by tracking daily price growth, given a starting price, but as suggested by AI, this was
needlessly complicated. Instead, the code now tracks the total shares owned in a given stock at a given time, and then knowing the closing price, the total value owned of a specific stock is known. Then, by summing over all
the stocks owned, the total portfolio value is known. Method in the class from construct_tracker() onwards were made by AI, but everything else was hand coded by me. The following output can be seen from this code:
<img width="1000" height="600" alt="Figure_1" src="https://github.com/user-attachments/assets/a57c8bf4-b044-441d-a4bb-1a0171c29c4b" />

