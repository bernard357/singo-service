
Feature: Profiles

  As a self-registered person
  Roger can access and delete his profile, but cannot change it
  so as to limit information that is exposed without control

  As a community member
  Marc can access, modify and delete his profile
  so as to enable members to manage their profiles by themselves

  As a community member
  Marc can access profiles of other members and board members, but cannot modify them nor delete them
  so as to keep control in small number of hands

  As a community leader
  Lea can access, modify and delete profiles of any registered person, community member or board member
  so as to manage information related to community members

  As a support engineer of the system
  Sylvia can access, modify and delete any profile
  so as to manage the entire community

  As a community software agent
  Robot cannot access, modify, or delete any profile
  so as to limit blast radius of automation

  As a community auditor
  Alfred can access any profile but not modify it nor delete it
  so as to observe the community


  Scenario: where Roger can read his profile but not more
    Given a surfer registered with e-mail 'roger@acme.com' and password 'P455w@rd' and persona 'registered'
    When surfer has been authenticated with 'roger@acme.com' and password 'P455w@rd'
    Then surfer is prevented to read the index of profiles
    And surfer can read profile of 'roger@acme.com'
    And surfer is prevented to modify profile of 'roger@acme.com'
    And surfer is prevented to delete profile of 'roger@acme.com'

  Scenario: where Roger is prevented to pollute profiles of other persons
    Given a person registered with identity <identity> and persona <persona>
    When a surfer registered as <actor> and <role>
    And surfer has been authenticated as <actor>
    Then surfer is prevented to read profile of <identity>
    And surfer is prevented to modify profile of <identity>
    And surfer is prevented to delete profile of <identity>

    Examples:
    | actor          | role       | identity         | persona    |
    | roger@acme.com | registered | peer@acme.com    | registered |
    | roger@acme.com | registered | marc@acme.com    | member     |
    | roger@acme.com | registered | lea@acme.com     | leader     |
    | roger@acme.com | registered | sylvia@acme.com  | support    |
    | roger@acme.com | registered | robot@acme.com   | robot      |
    | roger@acme.com | registered | alfred@acme.com  | audit      |


  Scenario: where Marc can manage his own profile
    Given a surfer registered with e-mail 'marc@acme.com' and password 'P455w@rd' and persona 'member'
    When surfer has been authenticated with 'marc@acme.com' and password 'P455w@rd'
    Then surfer can read the index of profiles
    And surfer can read profile of 'marc@acme.com'
    And surfer can modify profile of 'marc@acme.com'
    And surfer can delete profile of 'marc@acme.com'

  Scenario: where Marc is prevented to pollute profiles of other persons
    Given a person registered with identity <identity> and persona <persona>
    When a surfer registered as <actor> and <role>
    And surfer has been authenticated as <actor>
    Then surfer can read profile of <identity>
    And surfer is prevented to modify profile of <identity>
    And surfer is prevented to delete profile of <identity>

    Examples:
    | actor         | role   | identity         | persona    |
    | marc@acme.com | member | peer@acme.com    | member     |
    | marc@acme.com | member | lea@acme.com     | leader     |
    | marc@acme.com | member | alfred@acme.com  | audit      |

  Scenario: where Marc cannot interact with special profiles
    Given a person registered with identity <identity> and persona <persona>
    When a surfer registered as <actor> and <role>
    And surfer has been authenticated as <actor>
    Then surfer is prevented to read profile of <identity>
    And surfer is prevented to modify profile of <identity>
    And surfer is prevented to delete profile of <identity>

    Examples:
    | actor         | role   | identity         | persona    |
    | marc@acme.com | member | roger@acme.com   | registered |
    | marc@acme.com | member | sylvia@acme.com  | support    |
    | marc@acme.com | member | robot@acme.com   | robot      |


  Scenario: where Lea can manage her own profile
    Given a surfer registered with e-mail 'lea@acme.com' and password 'P455w@rd' and persona 'leader'
    When surfer has been authenticated with 'lea@acme.com' and password 'P455w@rd'
    Then surfer can read the index of profiles
    And surfer can read profile of 'lea@acme.com'
    And surfer can modify profile of 'lea@acme.com'
    And surfer can delete profile of 'lea@acme.com'

  Scenario: where Lea is allowed to manage most profiles
    Given a person registered with identity <identity> and persona <persona>
    When a surfer registered as <actor> and <role>
    And surfer has been authenticated as <actor>
    Then surfer can read profile of <identity>
    And surfer can modify profile of <identity>
    And surfer can delete profile of <identity>

    Examples:
    | actor        | role   | identity         | persona    |
    | lea@acme.com | leader | roger@acme.com   | registered |
    | lea@acme.com | leader | marc@acme.com    | member     |
    | lea@acme.com | leader | peer@acme.com    | leader     |
    | lea@acme.com | leader | alfred@acme.com  | audit      |


  Scenario: where Lea can not manage special profiles
    Given a person registered with identity <identity> and persona <persona>
    When a surfer registered as <actor> and <role>
    And surfer has been authenticated as <actor>
    Then surfer can read profile of <identity>
    And surfer is prevented to modify profile of <identity>
    And surfer is prevented to delete profile of <identity>

    Examples:
    | actor        | role   | identity         | persona    |
    | lea@acme.com | leader | sylvia@acme.com  | support    |


  Scenario: where Lea can not manage even see special profile
    Given a person registered with identity <identity> and persona <persona>
    When a surfer registered as <actor> and <role>
    And surfer has been authenticated as <actor>
    Then surfer is prevented to read profile of <identity>
    And surfer is prevented to modify profile of <identity>
    And surfer is prevented to delete profile of <identity>

    Examples:
    | actor        | role   | identity         | persona    |
    | lea@acme.com | leader | robot@acme.com   | robot      |


  Scenario: where Sylvia can manage her own profile
    Given a surfer registered with e-mail 'sylvia@acme.com' and password 'P455w@rd' and persona 'support'
    When surfer has been authenticated with 'sylvia@acme.com' and password 'P455w@rd'
    Then surfer can read the index of profiles
    And surfer can read profile of 'sylvia@acme.com'
    And surfer can modify profile of 'sylvia@acme.com'
    And surfer can delete profile of 'sylvia@acme.com'

  Scenario: where Sylvia is allowed to manage any profile
    Given a person registered with identity <identity> and persona <persona>
    When a surfer registered as <actor> and <role>
    And surfer has been authenticated as <actor>
    Then surfer can read profile of <identity>
    And surfer can modify profile of <identity>
    And surfer can delete profile of <identity>

    Examples:
    | actor           | role    | identity         | persona    |
    | sylvia@acme.com | support | roger@acme.com   | registered |
    | sylvia@acme.com | support | marc@acme.com    | member     |
    | sylvia@acme.com | support | lea@acme.com     | leader     |
    | sylvia@acme.com | support | peer@acme.com    | support    |
    | sylvia@acme.com | support | robot@acme.com   | robot      |
    | sylvia@acme.com | support | alfred@acme.com  | audit      |


  Scenario: where Robot can not even read his own profile
    Given a surfer registered with e-mail 'robot@acme.com' and password 'P455w@rd' and persona 'robot'
    When surfer has been authenticated with 'robot@acme.com' and password 'P455w@rd'
    Then surfer is prevented to read the index of profiles
    And surfer is prevented to read profile of 'robot@acme.com'
    And surfer is prevented to modify profile of 'robot@acme.com'
    And surfer is prevented to delete profile of 'robot@acme.com'

  Scenario: where Robot is prevented to pollute profiles of other persons
    Given a person registered with identity <identity> and persona <persona>
    When a surfer registered as <actor> and <role>
    And surfer has been authenticated as <actor>
    Then surfer is prevented to read profile of <identity>
    And surfer is prevented to modify profile of <identity>
    And surfer is prevented to delete profile of <identity>

    Examples:
    | actor          | role  | identity         | persona    |
    | robot@acme.com | robot | roger@acme.com   | registered |
    | robot@acme.com | robot | marc@acme.com    | member     |
    | robot@acme.com | robot | lea@acme.com     | leader     |
    | robot@acme.com | robot | sylvia@acme.com  | support    |
    | robot@acme.com | robot | peer@acme.com    | robot      |
    | robot@acme.com | robot | alfred@acme.com  | audit      |


  Scenario: where Alfred can read his profile but not manage it
    Given a surfer registered with e-mail 'alfred@acme.com' and password 'P455w@rd' and persona 'audit'
    When surfer has been authenticated with 'alfred@acme.com' and password 'P455w@rd'
    Then surfer can read the index of profiles
    And surfer can read profile of 'alfred@acme.com'
    And surfer is prevented to modify profile of 'alfred@acme.com'
    And surfer is prevented to delete profile of 'alfred@acme.com'

  Scenario: where Alfred is prevented to pollute profiles of other persons
    Given a person registered with identity <identity> and persona <persona>
    When a surfer registered as <actor> and <role>
    And surfer has been authenticated as <actor>
    Then surfer can read profile of <identity>
    And surfer is prevented to modify profile of <identity>
    And surfer is prevented to delete profile of <identity>

    Examples:
    | actor           | role  | identity         | persona    |
    | alfred@acme.com | audit | roger@acme.com   | registered |
    | alfred@acme.com | audit | marc@acme.com    | member     |
    | alfred@acme.com | audit | lea@acme.com     | leader     |
    | alfred@acme.com | audit | sylvia@acme.com  | support    |
    | alfred@acme.com | audit | robot@acme.com   | robot      |
    | alfred@acme.com | audit | peer@acme.com    | audit      |
