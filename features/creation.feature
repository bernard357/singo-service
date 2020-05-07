
Feature: Creation

  As an anonymous surfer
  Alice cannot create pages in any channel
  so as to only look for information

  As a self-registered person
  Roger cannot create pages in any channel
  so as to only connect with other members

  As a community member
  Marc cannot create pages in any channel
  so as to only connect with other members

  As a community leader
  Lea can create pages in any channel
  so as to lead the community

  As a community software agent
  Robot cannot create pages in any channel
  so as to limit blast radius of automation

  As a community auditor
  Alfred cannot create pages in any channel
  so as to ensure separation of duties

  As a support engineer of the system
  Sylvia can create pages in any channel
  so as to manage the entire community


  Scenario Outline: where user is prevented to create a page
    Given a user authenticated as <name> and as persona <persona>
    When the user <name> adds a page <title> to path <path>
    Then an error code is returned

    Examples:
    | name    | persona    | path        | title                |
    | Alice   | anonymous  | /           | surfer world         |
    | Alice   | anonymous  | /community/ | surfer community     |
    | Alice   | anonymous  | /board/     | surfer board         |
    | Roger   | registered | /           | registered world     |
    | Roger   | registered | /community/ | registered community |
    | Roger   | registered | /board/     | registered board     |
    | Marc    | member     | /           | member world         |
    | Marc    | member     | /community/ | member community     |
    | Marc    | member     | /board/     | member board         |
    | Alfred  | audit      | /           | auditor world        |
    | Alfred  | audit      | /community/ | auditor community    |
    | Alfred  | audit      | /board/     | auditor board        |
    | Robot   | robot      | /           | robot world          |
    | Robot   | robot      | /community/ | robot community      |
    | Robot   | robot      | /board/     | robot board          |


  Scenario Outline: where user adds pages to channels
    Given a user authenticated as <name> and as persona <persona>
    When the user <name> adds a page <title> to path <path>
    Then page <title> is listed first at path <path>

    Examples:
    | name    | persona   | path        | title             |
    | Lea     | leader    | /           | leader world      |
    | Lea     | leader    | /community/ | leader community  |
    | Lea     | leader    | /board/     | leader board      |
    | Sylvia  | support   | /           | support world     |
    | Sylvia  | support   | /community/ | support community |
    | Sylvia  | support   | /board/     | support board     |
