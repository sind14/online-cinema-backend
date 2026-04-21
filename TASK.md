# Online Cinema Assignment

## Table of Contents

- [General Description](#general-description)
- [Key Features](#key-features)
  - [1. Authorization and Authentication](#1-authorization-and-authentication)
  - [2. Movies](#2-movies)
  - [3. Shopping Cart](#3-shopping-cart)
  - [4. Orders](#4-orders)
  - [5. Payments](#5-payments)
  - [6. Docker and Docker Compose](#6-docker-and-docker-compose)
  - [7. Poetry for Dependency Management](#7-poetry-for-dependency-management)
  - [8. CI/CD with GitHub Actions](#8-cicd-with-github-actions)
  - [9. Swagger Documentation Requirements](#9-swagger-documentation-requirements)
  - [10. Writing Tests](#10-writing-tests)

## General Description

An online cinema is a digital platform that allows users to select, watch, and
purchase access to movies and other video materials via the internet.

These services have become popular due to their convenience, wide selection of
content, and the ability to personalize the user experience.

## Key Features

### 1. Authorization and Authentication

#### User Registration

- Users should be able to register using their email.
- After registration, an email is sent with a link to activate the account.
- If the user does not activate the account within 24 hours, the activation link
  becomes invalid.
- If the activation link expires, the user should be able to enter their email
  and receive a new activation link, valid for another 24 hours.
- Expired activation tokens should be periodically deleted using `celery-beat`.
- Email uniqueness must be checked before registration.

#### Login and Logout

- Users should be able to log in.
- Users should be able to log out.
- Logout should delete or revoke the user's JWT refresh token, making it unusable
  for future authentication.

#### Password Management

- Users can change their password if they remember the old password.
- Password change requires entering the old password and a new password.
- Users who forget their password can enter their email.
- If the email is registered and the account is active, a reset link is sent.
- The reset link allows users to set a new password without confirming the old
  password.
- Password complexity validation must be enforced.

#### JWT Token Management

- Users receive a pair of JWT tokens after login:
  - access token
  - refresh token
- Users can use the refresh token to obtain a new access token with a shorter
  time-to-live (TTL).

#### User Groups

The system should include three user groups:

- `USER`: access to the basic user interface.
- `MODERATOR`: can access the catalog and user interface, manage movies through
  the admin panel, view sales, and perform selected administrative actions.
- `ADMIN`: inherits all previous permissions and can manage users, change group
  memberships, and manually activate accounts.

#### Entities and Attributes

##### `UserGroupEnum`

Enumeration of possible user groups:

- `USER`: a regular user with basic interface access.
- `MODERATOR`: a user who can manage content, view sales, and perform selected
  administrative tasks.
- `ADMIN`: a user with extended rights who can manage other users, change groups,
  and manually activate accounts.

##### `GenderEnum`

Enumeration for storing a user's gender:

- `MAN`
- `WOMAN`

This field is optional.

##### `UserGroup` (`user_groups` table)

Stores user groups.

Attributes:

- `id`: primary key.
- `name`: unique group name (`USER`, `MODERATOR`, `ADMIN`).

Relationships:

- One `UserGroup` can be related to many `User` records.

##### `User` (`users` table)

Represents registered users.

Attributes:

- `id`: primary key.
- `email`: unique and required user email, used for login and identification.
- `hashed_password`: securely stored password hash.
- `is_active`: indicates whether the account is activated. Initially `False`;
  becomes `True` after activation.
- `created_at`: timestamp of when the user was created.
- `updated_at`: timestamp of the user's last data update.
- `group_id`: foreign key referencing `UserGroup`.

Relationships:

- Many users belong to one `UserGroup`.
- One user can have one `UserProfile`.
- One user can have many `ActivationToken`, `PasswordResetToken`, and
  `RefreshToken` records.

##### `UserProfile` (`user_profiles` table)

Stores additional user information.

Attributes:

- `id`: primary key.
- `user_id`: unique foreign key referencing `users`, creating a one-to-one
  relationship with `User`.
- `first_name`: user's first name, optional.
- `last_name`: user's last name, optional.
- `avatar`: link or identifier for the user's avatar.
- `gender`: optional gender value (`MAN` or `WOMAN`).
- `date_of_birth`: optional date of birth.
- `info`: short bio or additional user information.

Relationships:

- One-to-one with `User`.

##### `ActivationToken` (`activation_tokens` table)

Token for account activation, sent to the user's email after registration.

Attributes:

- `id`: primary key.
- `user_id`: unique foreign key referencing `users`.
- `token`: unique activation token.
- `expires_at`: expiration time, 24 hours after issuance.

Tasks:

- Create a new `ActivationToken` after registration.
- Mark the token as invalid after 24 hours.
- Allow resending a new token if the old one expires.
- Periodically remove expired tokens using `celery-beat`.

##### `PasswordResetToken` (`password_reset_tokens` table)

Token for resetting a forgotten password, sent to the user's email upon request.

Attributes:

- `id`: primary key.
- `user_id`: unique foreign key referencing `users`.
- `token`: unique password reset token.
- `expires_at`: token expiration time.

Tasks:

- Generate and send a reset token when a user requests password recovery.
- Allow the user to set a new password using the token.
- Validate the token expiration period.

##### `RefreshToken` (`refresh_tokens` table)

Refresh token used to obtain a new access token without re-entering login
credentials.

Attributes:

- `id`: primary key.
- `user_id`: foreign key referencing `users`.
- `token`: unique refresh token.
- `expires_at`: refresh token expiration time.

Tasks:

- Issue access and refresh tokens on login.
- Use the refresh token to issue a new access token.
- Delete the refresh token on logout.

#### Functional Requirements Summary

- Registration with an activation email.
- Account activation using the received token.
- Resending the activation token if the previous one expires.
- Periodic cleanup of expired activation tokens using `celery-beat`.
- Login that issues access and refresh JWT tokens.
- Logout that revokes the refresh token.
- Password reset with a token sent via email.
- Password complexity checks when changing or setting a new password.
- User groups with different permission levels: `USER`, `MODERATOR`, and `ADMIN`.
- Administrators can change a user's group and manually activate accounts.

### 2. Movies

#### User Functionality

- Browse the movie catalog with pagination.
- View detailed movie descriptions.
- Like or dislike movies.
- Write comments on movies.
- Filter movies by criteria such as release year or IMDb rating.
- Sort movies by attributes such as price, release date, or popularity.
- Search for movies by title, description, actor, or director.
- Add movies to favorites.
- Search, filter, and sort the favorites list.
- Remove movies from favorites.
- View a list of genres with the count of movies in each genre.
- Click a genre to view all related movies.
- Rate movies on a 10-point scale.
- Notify users when their comments receive replies or likes.

#### Moderator Functionality

- Perform CRUD operations on movies, genres, and actors.
- Prevent deleting a movie if at least one user has purchased it.

#### Entities and Attributes

##### `Genre` (`genres` table)

Represents a movie genre, such as Action, Drama, or Comedy.

Attributes:

- `id`: primary key.
- `name`: unique and required genre name.

Relationships:

- Many-to-many with `Movie` through the `movie_genres` association table.

##### `Star` (`stars` table)

Represents an actor or actress starring in a movie.

Attributes:

- `id`: primary key.
- `name`: unique and required star name.

Relationships:

- Many-to-many with `Movie` through the `movie_stars` association table.

##### `Director` (`directors` table)

Represents a movie director.

Attributes:

- `id`: primary key.
- `name`: unique and required director name.

Relationships:

- Many-to-many with `Movie` through the `movie_directors` association table.

##### `Certification` (`certifications` table)

Represents a movie rating or certification, such as `PG-13` or `R`.

Attributes:

- `id`: primary key.
- `name`: unique and required certification name.

Relationships:

- One certification can be applied to many movies.
- Each movie has exactly one certification.

##### `Movie` (`movies` table)

Represents the main movie data.

Attributes:

- `id`: primary key.
- `uuid`: globally unique movie UUID.
- `name`: required movie title.
- `year`: required release year.
- `time`: required duration in minutes.
- `imdb`: required IMDb rating.
- `votes`: required number of IMDb votes.
- `meta_score`: optional Metascore.
- `gross`: optional gross revenue.
- `description`: required synopsis or description.
- `price`: movie price as `DECIMAL(10, 2)`.
- `certification_id`: foreign key referencing `certifications.id`.

Constraints:

- Unique constraint on `name`, `year`, and `time`.

Relationships:

- Many-to-one with `Certification`.
- Many-to-many with `Genre` through `movie_genres`.
- Many-to-many with `Director` through `movie_directors`.
- Many-to-many with `Star` through `movie_stars`.

#### Association Tables

##### `movie_genres`

Connects `Movie` and `Genre`.

Columns:

- `movie_id`: foreign key to `movies.id`, part of the composite primary key.
- `genre_id`: foreign key to `genres.id`, part of the composite primary key.

##### `movie_directors`

Connects `Movie` and `Director`.

Columns:

- `movie_id`: foreign key to `movies.id`, part of the composite primary key.
- `director_id`: foreign key to `directors.id`, part of the composite primary
  key.

##### `movie_stars`

Connects `Movie` and `Star`.

Columns:

- `movie_id`: foreign key to `movies.id`, part of the composite primary key.
- `star_id`: foreign key to `stars.id`, part of the composite primary key.

### 3. Shopping Cart

#### User Functionality

- Users can add movies to the cart if they have not purchased them yet.
- If a movie has already been purchased, repeat purchase should not be allowed.
- Users can remove movies from the cart.
- Users can view a list of movies in their cart.
- For each cart movie, display the title, price, genre, and release year.
- Users can pay for all movies in the cart at once.
- After successful payment, movies are moved to the purchased list.
- Users can manually clear the entire cart.

#### Validation

- Ensure all movies are available for purchase before creating an order.
- Exclude already purchased movies and notify the user.
- Prompt unregistered users to sign up before completing a purchase.
- Prevent adding the same movie to the cart more than once.

#### Moderator Functionality

- Admins can view the contents of users' carts for analysis or troubleshooting.
- Moderators should be notified when attempting to delete a movie that exists in
  users' carts.

#### Entities and Attributes

##### `Cart` (`carts` table)

Represents a user's shopping cart. Each user can have exactly one cart.

Attributes:

- `id`: primary key.
- `user_id`: unique and required foreign key referencing `users.id`.

Relationships:

- One-to-one with `User`.
- One-to-many with `CartItem`.

Key points:

- The unique constraint on `user_id` guarantees that each user can have only one
  cart.
- The cart acts as a container for `CartItem` records.

##### `CartItem` (`cart_items` table)

Represents a single movie placed in a user's cart.

Attributes:

- `id`: primary key.
- `cart_id`: required foreign key referencing `carts.id`.
- `movie_id`: required foreign key referencing `movies.id`.
- `added_at`: timestamp of when the movie was added to the cart.

Relationships:

- Many-to-one with `Cart`.
- Many-to-one with `Movie`.

Constraints:

- Unique constraint on `cart_id` and `movie_id`.

#### Relationship Summary

- `User` -> `Cart`: one-to-one.
- `Cart` -> `CartItem`: one-to-many.
- `CartItem` -> `Movie`: many-to-one.

#### Functional Implications

- A user can manage their cart by adding, removing, or clearing items.
- A cart centralizes all movies the user wants to purchase.
- `CartItem` enforces movie uniqueness within a single cart.
- `CartItem.added_at` can be useful for UI features or analytics.

### 4. Orders

#### User Functionality

- Users can place orders for movies in their cart.
- If movies are unavailable, they are excluded from the order and the user is
  notified.
- Users can view a list of all their orders.
- Each order should display:
  - date and time
  - list of included movies
  - total amount
  - status (`paid`, `canceled`, or `pending`)
- After confirming an order, users are redirected to a payment gateway.
- Users can cancel orders before payment is completed.
- Once paid, orders can only be canceled through a refund request.
- After successful payment, users receive an email confirmation.

#### Validation

- Ensure the cart is not empty before placing an order.
- Exclude movies already purchased by the user.
- Ensure all movies in the order are available for purchase.
- Check that no other orders with the same movies are already pending.
- Revalidate the total amount before payment in case prices changed.

#### Moderator Functionality

Admins can view all user orders with filters by:

- users
- dates
- statuses

#### Entities and Attributes

##### `Order` (`orders` table)

Represents a user's order containing one or more movies.

Attributes:

- `id`: primary key.
- `user_id`: required foreign key referencing `users.id`.
- `created_at`: timestamp of when the order was created.
- `status`: order status.
- `total_amount`: total cost of all items at the time of order creation.

Possible order statuses:

- `pending`: the order has been placed but not paid yet.
- `paid`: the order has been successfully paid.
- `canceled`: the order has been canceled.

Relationships:

- One-to-many with `OrderItem`.
- Many-to-one with `User`.

Key points:

- `Order` stores a snapshot of what the user intends to purchase.
- `status` tracks the order lifecycle.
- `total_amount` can be checked or updated before finalizing payment.

##### `OrderItem` (`order_items` table)

Represents a single line item inside an order.

Attributes:

- `id`: primary key.
- `order_id`: required foreign key referencing `orders.id`.
- `movie_id`: required foreign key referencing `movies.id`.
- `price_at_order`: price of the movie at the time the order was created.

Relationships:

- Many-to-one with `Order`.
- Many-to-one with `Movie`.

Key points:

- `OrderItem` provides a breakdown of order contents.
- `price_at_order` ensures historical accuracy even if movie prices change later.

#### Relationship Summary

- `User` -> `Order`: one-to-many.
- `Order` -> `OrderItem`: one-to-many.
- `Movie` -> `OrderItem`: one-to-many.

#### Functional Implications

- Users can track order history.
- Order history includes purchased movies, final amount, and current status.
- `price_at_order` keeps financial records consistent over time.
- `status` supports payment, cancellation, and refund workflows.

### 5. Payments

#### User Functionality

- Users can make payments using Stripe.
- After payment, users receive confirmation on the website and by email.
- Users can view payment history.
- Payment history should include:
  - date and time
  - amount
  - status (`successful`, `canceled`, or `refunded`)

#### Validation

- Verify the total amount of the order.
- Check availability of the selected payment method.
- Ensure the user is authenticated.
- Validate transactions through payment system webhooks.
- Update the order status after successful payment.
- If a transaction is declined, display recommendations to the user.

#### Moderator Functionality

Admins can view a list of all payments with filters by:

- users
- dates
- statuses

#### Entities and Attributes

##### `Payment` (`payments` table)

Represents a payment transaction made by a user for an order.

Attributes:

- `id`: primary key.
- `user_id`: required foreign key referencing `users.id`.
- `order_id`: required foreign key referencing `orders.id`.
- `created_at`: timestamp of when the payment was created.
- `status`: current payment status.
- `amount`: total amount of the payment.
- `external_payment_id`: optional external transaction ID from the payment
  provider, such as Stripe.

Possible payment statuses:

- `successful`: the payment has been completed successfully.
- `canceled`: the payment was canceled before completion.
- `refunded`: the amount was refunded after a successful payment.

Relationships:

- Many-to-one with `User`.
- Many-to-one with `Order`.
- One-to-many with `PaymentItem`.

Key points:

- Payment records are financial transactions linked to orders.
- `external_payment_id` and `status` help integrate with external payment
  gateways.

##### `PaymentItem` (`payment_items` table)

Represents an individual item paid for in a single payment.

Attributes:

- `id`: primary key.
- `payment_id`: required foreign key referencing `payments.id`.
- `order_item_id`: required foreign key referencing `order_items.id`.
- `price_at_payment`: price of the order item at the time of payment.

Relationships:

- Many-to-one with `Payment`.
- Many-to-one with `OrderItem`.

Key points:

- `PaymentItem` captures item prices at the exact moment of payment.
- Itemized payments support reporting, refunds, reconciliation, and audits.

#### Relationship Summary

- `User` -> `Payment`: one-to-many.
- `Order` -> `Payment`: one-to-many.
- `Payment` -> `PaymentItem`: one-to-many.
- `OrderItem` -> `PaymentItem`: one-to-many.

#### Functional Implications

- Users have a clear history of all payments.
- Payment records include when, how much, and which items were paid for.
- `status` and `external_payment_id` support payment gateway integration.
- Detailed payment itemization supports audits and troubleshooting.

### 6. Docker and Docker Compose

#### Project Containerization

- Use Docker to containerize the project and manage related services efficiently.

#### Service Management

- Deploy multiple services using Docker Compose, such as:
  - FastAPI
  - Redis
  - Celery
  - MinIO

#### Custom Docker Images

- Create and maintain Docker images for the FastAPI application and related
  services.

#### Single Command Setup

- Use a single Docker Compose command to launch all services for development and
  deployment.

### 7. Poetry for Dependency Management

#### Dependency Simplification

- Use Poetry for dependency management and virtual environment handling.

#### Project Dependencies

- Install required project dependencies through Poetry commands.

#### Configuration File

- Use `pyproject.toml` to specify dependencies, versions, and additional project
  configuration.

#### Environment Management

- Manage virtual environments through the development workflow.

### 8. CI/CD with GitHub Actions

#### Automated Processes

- Configure GitHub Actions to automate code quality checks, testing, and
  deployment pipelines.

#### Code Quality Checks

- Run linters or formatters such as `flake8` or `black`.
- Perform type checking with `mypy`.

#### Testing Automation

- Execute tests using `pytest`.
- Generate and review code coverage reports.

#### Continuous Deployment

- Automatically deploy the application after checks pass and pull requests are
  merged to AWS EC2.

### 9. Swagger Documentation Requirements

#### OpenAPI Specification

- Use OpenAPI Specification version 3.0 or above.

#### Complete API Documentation

- Ensure all API endpoints are fully documented for developers and stakeholders.

#### Access Control

- Restrict access to API documentation so that only authorized users can view it.

### 10. Writing Tests

#### API Endpoint Testing

- Verify that endpoints return correct responses.
- Test error handling and proper feedback for invalid inputs.

#### Validation Testing

- Ensure business rules and validation logic work correctly, including:
  - authentication
  - filtering
  - sorting

#### Unit Tests

Cover:

- data validation logic
- utility functions
- individual business rules

#### Integration Tests

Cover:

- interaction between endpoints and the database
- authentication workflows
- JWT processing

#### Functional Tests

Cover end-to-end user scenarios such as:

- registration
- login
- movie filtering
- order placement
