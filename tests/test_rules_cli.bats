#!/usr/bin/env bats

@test "check-rules reports non-existent files" {
    run your5e check-rules nonexistent.md
    [ "$status" -eq 1 ]
    [[ "$output" == *"Error: 'nonexistent.md' not found"* ]]
}

@test "check-rules output matches reference" {
    run your5e check-rules rules/directives/hit_die.md
    [ $status -eq 1 ]
    diff -u tests/rules/directives/hit_die.txt <(echo "$output")
}

@test "check-rules verbose output matches reference" {
    run your5e check-rules --verbose rules/directives/hit_die.md
    [ $status -eq 1 ]
    diff -u tests/rules/directives/hit_die.verbose.txt <(echo "$output")
}

@test "check-rules with valid file gives no output" {
    run your5e check-rules tests/rules/all_good.md
    [ $status -eq 0 ]
    [ -z "$output" ]
}
