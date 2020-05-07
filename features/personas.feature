
Feature: Personas

  As a self-registered person
  Roger registers to the site
  so as to look for information and to be more involved

  As a community member
  Marc registers to the site and is upgraded by a community leader or by a support engineer
  so as to connect with other members

  As a community leader
  Lea registers to the site and is upgraded by another leader or by a support engineer
  so as to lead the community

  As a support engineer of the system
  Sylvia registers with shared secret
  so as to manage the entire community

  As a support engineer of the system
  Sylvia registers some community members or leaders
  so as to manage the entire community

  As a community software agent
  Robot is registered by a support engineer
  so as to limit blast radius of automation

  As a community auditor
  Alfred registers to the site and is upgraded by a support engineer
  so as to observe the community


  Scenario: where anonymous registers to the community
    Given a surfer navigating the site
    When surfer '-' registers with password 'P455w@rd'
    Then the operation is denied

  Scenario: where Roger registers to the community
    Given a surfer navigating the site
    When surfer 'Roger' registers with password 'P455w@rd'
    Then surfer 'Roger' has persona 'registered'

  Scenario: where Roger is prevented to promote a member
    Given a user authenticated as 'Roger' and as persona 'registered'
    When surfer 'William' registers with password 'P455w@rd'
    And user 'Roger' promotes 'William' to 'member'
    Then surfer 'William' does NOT have persona 'member'

  Scenario: where Roger is prevented to promote a leader
    Given a user authenticated as 'Roger' and as persona 'registered'
    When surfer 'William' registers with password 'P455w@rd'
    And user 'Roger' promotes 'William' to 'leader'
    Then surfer 'William' does NOT have persona 'leader'

  Scenario: where Marc becomes a community member from leader
    Given a user authenticated as 'Lea' and as persona 'leader'
    When surfer 'Marc' registers with password 'P455w@rd'
    And user 'Lea' promotes 'Marc' to 'member'
    Then surfer 'Marc' has persona 'member'

  Scenario: where Marc becomes a community member from support
    Given a user authenticated as 'Sylvia' and as persona 'support'
    When surfer 'Marc' registers with password 'P455w@rd'
    And user 'Sylvia' promotes 'Marc' to 'member'
    Then surfer 'Marc' has persona 'member'

  Scenario: where Marc is registered as community member by support
    Given a user authenticated as 'Sylvia' and as persona 'support'
    When user 'Sylvia' registers identity 'Marc' with password 'P455w@rd' and persona 'member'
    Then surfer 'Marc' has persona 'member'

  Scenario: where Marc is prevented to register a member
    Given a user authenticated as 'Marc' and as persona 'member'
    When user 'Marc' registers identity 'William' with password 'P455w@rd' and persona 'member'
    Then the operation is denied

  Scenario: where Marc is prevented to promote a member
    Given a user authenticated as 'Marc' and as persona 'member'
    When surfer 'William' registers with password 'P455w@rd'
    And user 'Marc' promotes 'William' to 'member'
    Then surfer 'William' does NOT have persona 'member'

  Scenario: where Marc is prevented to modify a registered profile
    Given a user authenticated as 'Marc' and as persona 'member'
    When surfer 'Roger' registers with password 'P455w@rd'
    And user 'Marc' modifies profile of 'Roger' with password 'modified'
    Then the operation is denied

  Scenario: where Marc is prevented to delete a registered profile
    Given a user authenticated as 'Marc' and as persona 'member'
    When surfer 'Roger' registers with password 'P455w@rd'
    And user 'Marc' deletes profile of 'Roger'
    Then the operation is denied

  Scenario: where Marc is prevented to promote a leader
    Given a user authenticated as 'Marc' and as persona 'member'
    When surfer 'William' registers with password 'P455w@rd'
    And user 'Marc' promotes 'William' to 'leader'
    Then surfer 'William' does NOT have persona 'leader'

  Scenario: where Lea becomes a community leader from peer
    Given a user authenticated as 'Peer' and as persona 'leader'
    When surfer 'Lea' registers with password 'P455w@rd'
    And user 'Peer' promotes 'Lea' to 'leader'
    Then surfer 'Lea' has persona 'leader'

  Scenario: where Lea becomes a community leader from support
    Given a user authenticated as 'Sylvia' and as persona 'support'
    When surfer 'Lea' registers with password 'P455w@rd'
    And user 'Sylvia' promotes 'Lea' to 'leader'
    Then surfer 'Lea' has persona 'leader'

  Scenario: where Lea is registered as community leader by support
    Given a user authenticated as 'Sylvia' and as persona 'support'
    When user 'Sylvia' registers identity 'Lea' with password 'P455w@rd' and persona 'leader'
    Then surfer 'Lea' has persona 'leader'

  Scenario: where Lea is prevented to promote a support person
    Given a user authenticated as 'Lea' and as persona 'leader'
    When surfer 'William' registers with password 'P455w@rd'
    And user 'Lea' promotes 'William' to 'support'
    Then surfer 'William' does NOT have persona 'support'

  Scenario: where Lea is prevented to promote a robot
    Given a user authenticated as 'Lea' and as persona 'leader'
    When surfer 'Robot' registers with password 'P455w@rd'
    And user 'Lea' promotes 'Robot' to 'robot'
    Then surfer 'Robot' does NOT have persona 'robot'

  Scenario: where Alfred becomes an auditor from leader
    Given a user authenticated as 'Lea' and as persona 'leader'
    When surfer 'Alfred' registers with password 'P455w@rd'
    And user 'Lea' promotes 'Alfred' to 'audit'
    Then surfer 'Alfred' has persona 'audit'

  Scenario: where Sylvia registers as support engineer
    Given a surfer navigating the site protected by secret 's3cret'
    When surfer 'Sylvia' registers with secret 's3cret' and password 'P455w@rd'
    Then surfer 'Sylvia' has persona 'support'

  Scenario: where credentials are given to Robot identity
    Given a user authenticated as 'Sylvia' and as persona 'support'
    When user 'Sylvia' registers identity 'Robot' with password 'P455w@rd' and persona 'robot'
    Then surfer 'Robot' has persona 'robot'

  Scenario: where Alfred becomes an auditor from support
    Given a user authenticated as 'Sylvia' and as persona 'support'
    When surfer 'Alfred' registers with password 'P455w@rd'
    And user 'Sylvia' promotes 'Alfred' to 'audit'
    Then surfer 'Alfred' has persona 'audit'

  Scenario: where Alfred is registered as community leader by support
    Given a user authenticated as 'Sylvia' and as persona 'support'
    When user 'Sylvia' registers identity 'Alfred' with password 'P455w@rd' and persona 'audit'
    Then surfer 'Alfred' has persona 'audit'
