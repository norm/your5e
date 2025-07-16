#!/usr/bin/env bats

@test "your5e with no arguments shows usage" {
    run your5e
    [ "$status" -eq 1 ]
    [[ "$output" == *"usage:"* ]]
}

@test "your5e with unknown command shows usage and error" {
    run your5e unknown-command
    [ "$status" -eq 2 ]
    [[ "$output" == *"usage:"* ]]
    [[ "$output" == *"invalid choice: 'unknown-command'"* ]]
}
