
Feature: Authorization

  As an anonymous surfer
  Alice navigates the universe channel
  so as to look for information and to be more involved

  As a self-registered person
  Roger navigates the universe channel
  so as to look for information and to be more involved

  As a community member
  Marc navigates the universe channel and the community channel
  so as to connect with other members

  As an community leader
  Lea navigates the universe channel, the community channel and the board channel
  so as to lead the community

  As a community software agent
  Robot can only navigate the universe channel
  so as to limit blast radius of automation

  As a community auditor
  Alfred navigates the universe channel, the community channel and the board channel
  so as to observe community activities

  As a support engineer of the system
  Sylvia can access any channel of the site
  so as to manage the entire community


  Scenario Outline: where user is entitled to navigate content
    Given a user authenticated as <name> and as persona <persona>
    When the user <name> visits the channel <channel>
    Then the user <name> is given access to the channel <channel>

    Examples:
    | name    | persona    | channel   |
    | Alice   | anonymous  | universe  |
    | Roger   | registered | universe  |
    | Marc    | member     | universe  |
    | Marc    | member     | community |
    | Lea     | leader     | universe  |
    | Lea     | leader     | community |
    | Lea     | leader     | board     |
    | Robot   | robot      | universe  |
    | Alfred  | audit      | universe  |
    | Alfred  | audit      | community |
    | Alfred  | audit      | board     |
    | Sylvia  | support    | universe  |
    | Sylvia  | support    | community |
    | Sylvia  | support    | board     |


  Scenario Outline: where user is prevented to navigate content
    Given a user authenticated as <name> and as persona <persona>
    When the user <name> visits the channel <channel>
    Then access to the channel <channel> is denied to <name>

    Examples:
    | name    | persona    | channel   |
    | Alice   | anonymous  | community |
    | Alice   | anonymous  | board     |
    | Roger   | registered | community |
    | Roger   | registered | board     |
    | Marc    | member     | board     |
    | Robot   | robot      | community |
    | Robot   | robot      | board     |


  Scenario Outline: where user is entitled to list community members
    Given a user authenticated as <name> and as persona <persona>
    When the user <name> visits the community index
    Then the user <name> can list profiles

    Examples:
    | name    | persona    |
    | Marc    | member     |
    | Lea     | leader     |
    | Sylvia  | support    |
    | Alfred  | audit      |


  Scenario Outline: where user is prevented to list community members
    Given a user authenticated as <name> and as persona <persona>
    When the user <name> visits the community index
    Then list of profiles is denied to <name>

    Examples:
    | name    | persona    |
    | Alice   | anonymous  |
    | Roger   | registered |
    | Robot   | robot      |
