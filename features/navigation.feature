
Feature: Navigation

  As end user of the system
  I want to fetch data progressively by chunks
  so as to improve response time while enabling deep dives


  Scenario Outline: where user paginates available content
    Given a content of 57 pages and chunks of 12 pages
    When the user fetches pages with token <token>
    Then the user gets <count> pages and get updated token <next>

    Examples:
    | count | token                   | next                           |
    | 12    | None                    | /page/aGVsbG8gdGhlcmUxMg%3D%3D |
    | 12    | aGVsbG8gdGhlcmUxMg==    | /page/aGVsbG8gdGhlcmUyNA%3D%3D |
    | 12    | aGVsbG8gdGhlcmUyNA==    | /page/aGVsbG8gdGhlcmUzNg%3D%3D |
    | 12    | aGVsbG8gdGhlcmUzNg==    | /page/aGVsbG8gdGhlcmU0OA%3D%3D |
    | 9     | aGVsbG8gdGhlcmU0OA==    | EOF                            |


  Scenario Outline: where user paginates list of community members
    Given a community of 36 persons and chunks of 10 records
    When the user fetches profiles with token <token>
    Then the user gets <count> profiles and get updated token <next>

    Examples:
    | count | token             | next                       |
    | 10    | None              | /users/page/YXplcnR5MTA%3D |
    | 10    | YXplcnR5MTA=      | /users/page/YXplcnR5MjA%3D |
    | 10    | YXplcnR5MjA%3D    | /users/page/YXplcnR5MzA%3D |
    | 7     | YXplcnR5MzA%3D    | EOF                        |
