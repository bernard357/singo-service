
Feature: Maintenance

  As a community leader
  Lea can not load data from files
  so as to limit blast radius of mistakes

  As a community leader
  Lea can dump data to files
  so as to contribute to data protection

  As a community software agent
  Robot can load data from files
  so as to set the system to a given state

  As a community software agent
  Robot can dump data to files
  so as to take a snapshot of system state

  As a system auditor
  Alfred can not load data from files
  so as to limit blast radius of mistakes

  As a system auditor
  Alfred can dump data to files
  so as to take a snapshot of system state

  As a support engineer of the system
  Sylvia can load data from files
  so as to set or restore the system to a given state

  As a support engineer of the system
  Sylvia can dump data to files
  so as to take a snapshot of system state

  Scenario: where Marc is prevented to set system state from external files
    Given a set of external files representing a state of the system
    When the user authenticates as persona 'member'
    Then the agent is prevented to load external files into the system

  Scenario: where Marc is prevented to make a snapshot of system state
    Given a system in a given state
    When the user authenticates as persona 'member'
    Then the agent is prevented to dump system state to external files

  Scenario: where Lea is prevented to set system state from external files
    Given a set of external files representing a state of the system
    When the user authenticates as persona 'leader'
    Then the agent is prevented to load external files into the system

  @slow
  Scenario: where Lea makes a snapshot of system state
    Given a system in a given state
    When the user authenticates as persona 'leader'
    Then the agent can dump system state to external files

  @slow
  Scenario: where automated pipeline sets system state from external files
    Given a set of external files representing a state of the system
    When the robot has been authenticated as persona 'robot'
    Then the agent can load external files into the system

  @slow
  Scenario: where automated pipeline makes a snapshot of system state
    Given a system in a given state
    When the robot has been authenticated as persona 'robot'
    Then the agent can dump system state to external files

  Scenario: where Alfred is prevented to set system state from external files
    Given a set of external files representing a state of the system
    When the user authenticates as persona 'audit'
    Then the agent is prevented to load external files into the system

  @slow
  Scenario: where Alfred makes a snapshot of system state
    Given a system in a given state
    When the user authenticates as persona 'audit'
    Then the agent can dump system state to external files

  Scenario: where Sylvia sets system state from external files
    Given a set of external files representing a state of the system
    When the user authenticates as persona 'support'
    Then the agent can load external files into the system

  @slow
  Scenario: where Sylvia makes a snapshot of system state
    Given a system in a given state
    When the user authenticates as persona 'support'
    Then the agent can dump system state to external files

  Scenario: where connectivity can be checked remotely
    Given a system in a given state
    When the path '/ping' is requested over the web
    Then system responds with message 'pong' in JSON
