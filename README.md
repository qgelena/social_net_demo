# social_net_demo

A REST API demo for a very simplistic "social network", using Flask, SQLAlchemy and JWT.

Models:
- User
- Post (always made by a user)

Functionality:
- user signup: `POST /signup` with payload `{"username": "...", "password": "..."}`;
- user login: `POST /login` with payload `{"username": "...", "password": "..."}`, returns a JWT access token;
- post creation: `POST /newpost` with payload `{"content": "..."}` (JWT authorization is mandatory).
- post like: `POST /like/<post_id>` (JWT authorization is mandatory).
- post unlike: `POST /unlike/<post_id>` (JWT authorization is mandatory).
- analytics about how many likes was made: `GET /analytics?date_from=YYYY-MM-DD&date_to=YYYY-MM-DD`. API returns likes count aggregated by day.
- user activity tracking and reporting: `GET /activity/<user_id>` reports `{"last_login_time": "...", "last_request_time": "..."}` for a user.
