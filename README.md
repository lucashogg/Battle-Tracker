# Battle Tracker

> This is my final project for the course: CS50

## Short Description

Welcome to Battle Tracker!

Battle Tracker is a web app designed to assist the GM of a Dungeons and Dragons table top campaign. Battle Tracker will store unique characters or monsters each containing a few basic stats while keeping track of initiative in battles.

## Features

This project consists of utilizng [Flask](https://flask.palletsprojects.com/en/2.3.x/) in a [Python](https://www.python.org/) environment. All data is managed using [SQLite3](https://docs.python.org/3/library/sqlite3.html).

## How does this work?

Battle Tracker allows users to register a unique account which stores all of their data in three sqlite tables within battletracker.db:

-   users
    -   Stores username and hashed password
-   characters
    -   Stores characters and related stats that the user inputs
-   current_battle
    -   Stores character information while being used in the current battle

### Register

Registering an account creates a new user, which must be unique, and stores a hashed password via Flask `werkzeug.security`'s `generate_password_hash` upon creation.

![register](https://github.com/lucashogg/Battle-Tracker/assets/73367876/25926590-10bc-488d-b24a-3ef4aed90f5e)

### Login

A user is required to log into the web app providing their user name and password. Thanks to `werkzeug.security`'s `check_password_hash` we are able to check if the user input matches the stored password.

Upon a successful check, a Flask `session` is created with a randomly generated `app.secret_key` that saves a session cookie in the browser while the user is logged in.

![login](https://github.com/lucashogg/Battle-Tracker/assets/73367876/2aeea0a2-6f1f-4828-89fc-94ac6b1acda9)

### Add

The Add page allows users to add unique characters to their roster. Upon filling out the required fields, a character is created in the characters table and matched to the user's unique id. This allows for correct querying throughout the rest of the app.

![add](https://github.com/lucashogg/Battle-Tracker/assets/73367876/a8b323f8-8e8a-432f-af40-72230e8daef7)

### Characters

The Characters page allows users to view, edit, or delete a character from their roster. When a character is selected, the database is queryied using the user's unique id and then matching with name of the selected character.

![characters](https://github.com/lucashogg/Battle-Tracker/assets/73367876/b86aea74-a930-4e35-93df-b4581b184d52)

### Index (Home)

The Index, or Home page, brings everything together. Here a user can select characters from their roster to participate in a battle. Once characters are selected added via the dropdown they will appear in the table below. The user can then "Roll For Initiative" by click the button. This generates a random number between 1 and 20 while adding each specific character's modififier to the total. The characters are then sorted in descending order, allowing the user to determine which character starts first and so forth.

During battle a character might receive damage or healing. To account for this the user can input a negative (damage) or positive (healing) value under the Damage/Healing column. Once clicking Submit, the Current HP value will reflect the change. If the damage is subtracts greater than "0", the value will stay at "0."

A character might receive a special condition during battle. To account for this the user can select character and condition, click Add, and the condition will appear under the Condition column. To remove, follow the same instructions, but click "Remove."

Finally, to remove characters from battle, simply click the corresponding "X" button for a character and it will remove it from the table.

![index](https://github.com/lucashogg/Battle-Tracker/assets/73367876/344758a2-ac99-40cc-9f09-bba4eb39f484)

### Logout

If a user is logged out the `session` is cleared.

## Video Demo

[Battle Tracker](https://youtu.be/LeWseRsh2qk)
