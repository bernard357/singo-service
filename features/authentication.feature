
Feature: Authentication

  As a known member of the community
  Marc provides credentials or signature to authenticate
  so as to get a bearer for interacting with the system

  As a trusted software agent
  Robot provides credentials or signature to authenticate
  so as to get a bearer for interacting with the system


  Scenario Outline: where valid credentials are authenticated
    Given a user record has identity <identity> and password <password> and persona <persona>
    When the user authenticates successfully with identity <label> and password <secret>
    Then the bearer is for identity <identity> and persona <persona>

    Examples:
    | identity | password | persona | label | secret   |
    | Marc     | P455w@rd | member  | Marc  | P455w@rd |
    | Robot    | P455w@rd | robot   | Robot | P455w@rd |

  Scenario Outline: where invalid credentials are dismissed
    Given a user record has identity <identity> and password <password> and persona <persona>
    When the user fails to authenticate with identity <label> and password <secret>
    Then there is no valid bearer

    Examples:
    | identity | password | persona | label | secret   |
    | Marc     | P455w@rd | member  | Marc  | _aliens_ |
    | Robot    | P455w@rd | robot   | Alien | P455w@rd |

  Scenario Outline: where valid signature is authenticated
    Given a user record has identity <identity> and password <password> and persona <persona>
    When the user authenticates successfully with identity <identity> and hash <hash> and delta <delta>
    Then the bearer is for identity <identity> and persona <persona>

    Examples:
    | identity | password | persona | hash                             | delta |
    | Marc     | P455w@rd | member  | 5b49d1280e8517e54daeeb90034334ae | 0     |
    | Marc     | P455w@rd | member  | 5b49d1280e8517e54daeeb90034334ae | -1000 |
    | Marc     | P455w@rd | member  | 5b49d1280e8517e54daeeb90034334ae | +1000 |
    | Robot    | P455w@rd | robot   | 5b49d1280e8517e54daeeb90034334ae | 0     |
    | Robot    | P455w@rd | robot   | 5b49d1280e8517e54daeeb90034334ae | -1000 |
    | Robot    | P455w@rd | robot   | 5b49d1280e8517e54daeeb90034334ae | +1000 |

  Scenario Outline: where invalid signature is dismissed
    Given a user record has identity <identity> and password <password> and persona <persona>
    When the user fails to authenticate with identity <label> and hash <hash> and delta <delta>
    Then there is no valid bearer

    Examples:
    | identity | password | persona | label | hash                             | delta |
    | Marc     | P455w@rd | member  | Alien | 5b49d1280e8517e54daeeb90034334ae | 0     |
    | Marc     | P455w@rd | member  | Alien | 5b49d1280e8517e54daeeb90034334ae | -1000 |
    | Marc     | P455w@rd | member  | Alien | 5b49d1280e8517e54daeeb90034334ae | +1000 |
    | Marc     | P455w@rd | member  | Marc  | _fake_secret_7e54daeeb90034334ae | 0     |
    | Marc     | P455w@rd | member  | Marc  | _fake_secret_7e54daeeb90034334ae | -1000 |
    | Marc     | P455w@rd | member  | Marc  | _fake_secret_7e54daeeb90034334ae | +1000 |
    | Robot    | P455w@rd | robot   | Robot | _fake_secret_7e54daeeb90034334ae | 0     |
    | Robot    | P455w@rd | robot   | Robot | _fake_secret_7e54daeeb90034334ae | -1000 |
    | Robot    | P455w@rd | robot   | Robot | _fake_secret_7e54daeeb90034334ae | +1000 |

  Scenario Outline: where invalid bearer is dismissed
    Given a secret '5b49d1280e8517e54daeeb90034334ae' and validity of 60 minutes and expiration after 720 minutes
    When a bearer is submitted with identity <identity> and secret <secret> and delta <delta>
    Then the submitted bearer is for <label> and is <valid> and <renewable>

    Examples:
    | identity | secret                           | delta | label   | valid | renewable |
    | Marc     | 5b49d1280e8517e54daeeb90034334ae | 0     | Marc    | Yes   | Yes       |
    | Marc     | 5b49d1280e8517e54daeeb90034334ae | -2    | Marc    | Yes   | Yes       |
    | Marc     | 5b49d1280e8517e54daeeb90034334ae | -50   | Marc    | Yes   | Yes       |
    | Marc     | 5b49d1280e8517e54daeeb90034334ae | -120  | Marc    | No    | Yes       |
    | Marc     | 5b49d1280e8517e54daeeb90034334ae | -710  | Marc    | No    | Yes       |
    | Marc     | 5b49d1280e8517e54daeeb90034334ae | -730  | Marc    | No    | No        |
    | Marc     | 5b49d1280e8517e54daeeb90034334ae | -9000 | Marc    | No    | No        |
    | Marc     | 5b49d1280e8517e54daeeb90034334ae | +2    | Marc    | Yes   | Yes       |
    | Marc     | 5b49d1280e8517e54daeeb90034334ae | +40   | Marc    | No    | No        |
    | Marc     | 5b49d1280e8517e54daeeb90034334ae | +120  | Marc    | No    | No        |
    | Marc     | _fake_secret_7e54daeeb90034334ae | 0     | -       | No    | No        |
    | Lea      | 5b49d1280e8517e54daeeb90034334ae | 0     | Lea     | Yes   | Yes       |
    | Lea      | 5b49d1280e8517e54daeeb90034334ae | -70   | Lea     | No    | Yes       |
    | Lea      | _fake_secret_7e54daeeb90034334ae | 0     | -       | No    | No        |

  Scenario Outline: where bearer is renewed
    Given a secret '5b49d1280e8517e54daeeb90034334ae' and validity of 60 minutes and expiration after 720 minutes
    When a bearer is submitted with identity <identity> and secret <secret> and delta <delta>
    And the submitted bearer is renewed
    Then the renewed bearer is for <identity> and is valid and renewable

    Examples:
    | identity | secret                           | delta |
    | Marc     | 5b49d1280e8517e54daeeb90034334ae | 0     |
    | Marc     | 5b49d1280e8517e54daeeb90034334ae | -2    |
    | Marc     | 5b49d1280e8517e54daeeb90034334ae | -50   |
    | Marc     | 5b49d1280e8517e54daeeb90034334ae | -120  |
    | Marc     | 5b49d1280e8517e54daeeb90034334ae | -710  |
    | Marc     | 5b49d1280e8517e54daeeb90034334ae | +2    |

  Scenario Outline: where bearer cannot be renewed
    Given a secret '5b49d1280e8517e54daeeb90034334ae' and validity of 60 minutes and expiration after 720 minutes
    When a bearer is submitted with identity <identity> and secret <secret> and delta <delta>
    And the submitted bearer is renewed
    Then there is no valid bearer

    Examples:
    | identity | secret                           | delta |
    | Marc     | 5b49d1280e8517e54daeeb90034334ae | -730  |
    | Marc     | 5b49d1280e8517e54daeeb90034334ae | -9000 |
    | Marc     | 5b49d1280e8517e54daeeb90034334ae | +40   |
    | Marc     | 5b49d1280e8517e54daeeb90034334ae | +120  |
