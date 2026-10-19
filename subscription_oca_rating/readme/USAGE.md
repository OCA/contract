To collect ratings on subscriptions:

1.  Open a subscription. Use the *Send rating request* button in the
    header to email the customer a rating request. The email contains
    smiley links (*satisfied / okay / dissatisfied*) that let the
    customer rate the subscription.
2.  A rating request is also sent **automatically when the subscription
    is closed** (both from the close wizard and from the cron), provided
    the customer has an email address.
3.  Once the customer rates, the *Ratings* smart button shows the number
    of ratings for that subscription, and the *With ratings* filter lets
    you find rated subscriptions.

Notes:

-   The rating link (`/rate/<token>`) is served by the *Portal Ratings*
    (`portal_rating`) module. Install it if you want the full web rating
    page; the rating request and token are created regardless.
-   The person being rated (operator) is the subscription's commercial
    agent.
