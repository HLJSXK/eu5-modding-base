# European Universalis 5 Modding Knowledge Base

**Author:** Manus AI
**Date:** Jan 22, 2026

> **Note:** Generated 2026-01-22 as a baseline reference. May not reflect recent patches. Treat as background reading, not authoritative syntax — use `reference_official_defines/` and `reference_game_files/` to verify.

## 1. Introduction

European Universalis 5 (EU5), released in November 2025, is a grand strategy game developed by Paradox Development Studio. Built upon an updated version of the Clausewitz Engine and featuring the Jomini scripting layer, EU5 offers a powerful and flexible platform for modding. This document provides a comprehensive overview of the EU5 modding landscape, covering everything from fundamental concepts to advanced techniques, to serve as a foundational knowledge base for your modding projects.

## 2. Game Architecture

Understanding the technical foundation of EU5 is crucial for effective modding. The game's architecture is composed of two primary components: the Clausewitz Engine and the Jomini scripting layer.

*   **Clausewitz Engine**: This is the core game engine that handles the underlying systems, rendering, and performance. The version used in EU5 features significant improvements over its predecessors, including better multi-core support, which addresses some of the performance bottlenecks present in earlier Paradox titles like EU4. [1]
*   **Jomini Scripting Layer**: Jomini serves as an intermediate layer between the Clausewitz Engine and the game's content. It provides a standardized set of scripting tools and a scripting language that is shared across several modern Paradox titles, including Crusader Kings 3 and Victoria 3. This shared foundation means that experience with modding these other games is often transferable to EU5. [2]

## 3. Getting Started with Modding

This section outlines the initial steps to set up your development environment and create your first mod.

### 3.1. Development Environment

A proper development environment can significantly streamline the modding process. The recommended setup involves a source code editor with support for Paradox scripting languages.

| Editor                  | Recommended Extensions         | Notes                                                                 |
| ----------------------- | ------------------------------ | --------------------------------------------------------------------- |
| **Visual Studio Code**  | CwTools, Paradox Highlight     | Free, powerful, and the most popular choice for Paradox modding.        |
| **IntelliJ IDEA**       | Paradox Language Support       | Community Edition is free and offers robust features.                 |
| **Notepad++**           | (Custom Language File)         | A lightweight alternative, suitable for minor edits.                  |

### 3.2. Creating a New Mod

All mods are located in the `Documents/Paradox Interactive/Europa Universalis V/mod` directory. Each mod must have its own subfolder, which serves as the mod's root directory.

### 3.3. Debugging and Console Commands

EU5 includes a robust debug mode that is indispensable for mod development. To enable it, add the `-debug_mode` launch option in Steam. This provides access to the in-game console and enables hot-reloading, which applies script changes without restarting the game.

Key console commands for modders include:

*   `script_docs`: Generates documentation for effects, triggers, and scopes.
*   `dump_data_types`: Generates documentation for GUI scripting.
*   `error.log`: The primary log file for identifying script errors, located in `Documents/Paradox Interactive/Europa Universalis V/logs`.

## 4. Practical Mod Anatomy: A Community-Based Analysis

To supplement the theoretical concepts, an analysis was conducted on a sample of 16 community mods from the Steam Workshop. This analysis revealed common structures and best practices that serve as a practical guide for new modders. [3]

### 4.1. Standard Directory Structure

The analysis shows a consistent top-level directory structure. While only the `.metadata` directory is strictly mandatory, a typical mod utilizes several other folders to organize its content.

```
/my_mod_name
├── .metadata/          # (Mandatory) Contains metadata.json for the launcher
├── in_game/            # (Optional) Core gameplay files (scripts, events, GUI)
├── main_menu/          # (Optional) Localization and main menu graphics
├── loading_screen/     # (Optional) Custom loading screen assets
└── thumbnail.png       # (Optional) Preview image for the launcher
```

### 4.2. The `metadata.json` File

This file, located in the `.metadata` directory, is essential for the game to recognize and load the mod. It contains key information that is displayed in the game launcher.

| Key                      | Type    | Description                                                               |
| ------------------------ | ------- | ------------------------------------------------------------------------- |
| `name`                   | String  | The display name of the mod.                                              |
| `id`                     | String  | A unique identifier, often in the format `author.modname`. Can be empty.  |
| `version`                | String  | The version number of the mod (e.g., "1.0.0").                            |
| `supported_game_version` | String  | The compatible game version (e.g., "1.0.7" or "1.*.*").                   |
| `short_description`      | String  | A brief description, which can include BBCode for formatting on Steam.    |
| `tags`                   | Array   | A list of strings categorizing the mod (e.g., "Gameplay", "Graphics").    |
| `relationships`          | Array   | A list of mod dependencies. Usually empty for standalone mods.            |
| `game_custom_data`       | Object  | Contains game-specific flags, such as `"multiplayer_synchronized": true`. |
| `picture` / `thumbnail`  | String  | The filename of the mod's preview image (e.g., "thumbnail.png").        |

### 4.3. Content Directory Deep Dive

The `in_game` and `main_menu` folders are the heart of most mods, containing the files that alter game content.

*   **/in_game/**: This folder mirrors the game's own file structure for core mechanics. The most frequently used subfolder is `common`, which houses scripts for a vast array of game features, from government reforms to unit types.
*   **/main_menu/**: This folder primarily contains `localization` files, which handle all in-game text, and `gfx` files for custom graphics and interface elements.

#### International Organization Icons

The shared IO UI calls `InternationalOrganization.GetIcon` in common organization panels and tooltips. For a mod-defined international organization, provide a DDS file at:

```
main_menu/gfx/interface/icons/international_organizations/<io_type>.dds
```

The filename should match the `common/international_organizations` type key, such as `tv_arts_exhibition.dds`. Without this matching texture, shared UI surfaces fall back to the generic international organization icon even if a custom organization panel displays another texture locally.

#### International Organization Member Opinion Biases

The IO type readme documents automatic opinion and trust modifiers for fellow members. For each mod-defined IO type, define a matching `io_opinion_<io_type>` entry under `in_game/common/biases/` and localize the same key in `main_menu/localization`.

```pdx
io_opinion_tv_trade_league = {
    value = 10
}
```

If the bias is missing, startup logs can report that the international organization type needs an opinion of other members. Existing TV IOs usually use small positive values such as 10, while stronger alliance-like systems may use a higher value by design.

#### Production Method Base Profit

EU5 checks production-method base profit at startup using each involved good's `default_market_price`. If the output value is too high relative to the input value, the engine logs an error from `production_methods.cpp` that the production method has too high base profit and should be no more than 30%.

When tuning a recipe, compute:

```
input value = sum(input amount * input good default_market_price)
output value = output amount * produced good default_market_price
profit = (output value - input value) / input value
```

Keep `profit < 0.30`. For example, a recipe that outputs one 5-value good needs input value greater than 3.8462. The Wonder Material Workshop uses 1.54 lumber, 0.77 stone, and 0.77 masonry for one `tv_wonder_materials`, giving 3.85 input value and about 29.87% base profit.

#### Country Interaction Potential Scope

In `common/country_interactions`, `potential` documents the acting country as `scope:actor`. Do not put country-scoped IO membership iterators directly under `potential`; wrap them in `scope:actor`:

```pdx
potential = {
    scope:actor = {
        any_international_organizations_member_of = {
            international_organization_type = international_organization_type:tv_diplomatic_alliance
            leader_country ?= scope:actor
        }
    }
}
```

Direct `any_international_organizations_member_of` under `potential` can evaluate from an invalid root and log inconsistent trigger scopes (`invalid vs. country`). Vanilla `bribe_voter_for_policy` uses `scope:actor = { any_international_organizations_member_of = { ... } }` in its country interaction potential.

#### Country Interaction Selection Pre-Evaluation

Country interactions opened from panel buttons can evaluate `accept` scoring before a `select_trigger` has populated `scope:recipient`. Guard direct recipient reads inside `accept` with `exists = scope:recipient`, as vanilla `invite_settlers` does:

```pdx
accept = {
    if = {
        limit = { exists = scope:recipient }
        add = {
            desc = "THEIR_OPINION_TOOLTIP"
            value = "scope:recipient.opinion(scope:actor)"
        }
    }
}
```

The same interaction may also preview or walk `effect` before a selected target exists, so effect bodies that pass `scope:recipient` into IO membership changes should put the real mutation behind `if = { limit = { exists = scope:recipient } ... }`. Any actor-owned variable used by `accept` should be initialized at the lifecycle point that creates the feature; if an existing script can still evaluate before initialization, gate the value read with `scope:actor = { has_variable = <var> }` rather than reading `scope:actor.var:<var>` directly.

#### International Organization Monthly Effects and Tooltips

The shared IO tooltip can render visible children of an IO type's `monthly_effect` block. For internal monthly maintenance such as state repair, variable smoothing, member cleanup, or cached GUI refreshes, wrap the logic in `hidden_effect`:

```pdx
monthly_effect = {
    hidden_effect = {
        # maintenance logic
    }
}
```

Vanilla IOs such as HRE and Union use this pattern. Keep `monthly_change` entries visible when the player should see an IO variable's monthly breakdown; use `hidden_effect` for non-player-facing `monthly_effect` logic.

High-cardinality generated maintenance can still be too expensive on an IO type even when hidden. The Trade League monopoly system is the current exception: do not put its per-good monopoly refresh in `tv_trade_league.monthly_effect`. Dispatch it from `monthly_country_pulse`, save the current country scope, iterate `every_international_organizations_member_of` filtered to `tv_trade_league` and `leader_country ?= <saved country>`, then call the IO-scoped refresh from inside the matching IO.

`monthly_change` is evaluated from the IO variable's international-organization context. Do not reuse country-scoped scripted triggers there if they depend on `root.var:X`; nesting the call inside `leader_country ?= { ... }` does not make `root` become the country. Instead, keep country-state checks inside `leader_country ?= { ... }` and perform IO-variable comparisons from the IO scope, for example `var:stockpile >= leader_country.var:monthly_cost`.

The scripted-value tree is also the visible monthly breakdown. For a contribution that can be
positive or negative, do not put both cases inside one named `add` and conditionally apply an
anonymous `multiply = -1`; tooltip evaluation can expose that internal sign operation as a
spurious negative line with `missing tooltip`. Give each sign its own desc-bearing node under an
outer condition, using a positive magnitude in both branches:

```pdx
if = {
    limit = { leader_country ?= { var:stance ?= 1 } }
    add = { desc = "CONTRIBUTOR" value = 0.5 }
}
if = {
    limit = { leader_country ?= { var:stance ?= 2 } }
    subtract = { desc = "CONTRIBUTOR" value = 0.5 }
}
```

This mirrors vanilla's signed IO contribution structure in
`common/international_organizations/catholic_church.txt`.

#### International Organization Trigger Iterators

In scripted triggers, `any_international_organizations_member_of` is a trigger iterator. Put IO filters directly in the iterator block:

```pdx
any_international_organizations_member_of = {
    international_organization_type = international_organization_type:tv_arts_exhibition
    resolution_is_active = resolution:policy_vote
}
```

Do not add an effect-style `limit = { ... }` block here. The engine treats `limit` as a trigger clause in this context and logs `Unknown trigger type: limit`. Reserve `limit = {}` for effect iterators such as `every_international_organizations_member_of` when applying effects.

The inverse is also true in scripted effects: `any_international_organizations_member_of` is not an effect iterator. If an effect needs to enter matching IO scopes, use:

```pdx
every_international_organizations_member_of = {
    limit = {
        international_organization_type = international_organization_type:tv_trade_league
        leader_country ?= scope:saved_country
    }
    # effect body here
}
```

Using `any_international_organizations_member_of = { limit = { ... } ... }` directly in an effect body logs `Unknown effect any_international_organizations_member_of`.

#### International Organization Member Tenure

EU5 tracks how long a country has belonged to each international organization instance. In a country scope, use the native trigger:

```pdx
years_in_international_organization = {
    international_organization = prev
    value >= 5
}
```

`international_organization` must point at the IO instance being checked. In an IO-root `every_international_organization_member` iterator, vanilla uses `international_organization = root`; when a TV effect iterates `every_international_organizations_member_of` from a country and then enters a member-country scope, `prev` can point back to the iterated IO. For scoring, vanilla also exposes the script value form, e.g. `"scope:recipient.years_in_international_organization(scope:actor.union)"`.

Prefer this built-in tenure value for mechanics such as "member must have belonged to this alliance for at least 5 years" instead of adding monthly countdown variables or custom join-date state.

#### Scripted Trigger and Effect File Boundaries

`common/scripted_triggers` and `common/scripted_effects` are separate top-level databases. EU5 parses every top-level block in a `common/scripted_effects` file as a scripted effect. Do not emit `_trigger = { ... }` definitions into scripted-effect files, even if those blocks are only called from effect `limit` clauses. Move those blocks to `common/scripted_triggers`; otherwise trigger-only clauses such as `has_variable`, `religious_unity`, `always`, or trigger iterators are parsed as effect commands and log `Unknown effect ...` during startup.

The reverse context rule also applies inside a scripted trigger: `if`, `else_if`, and `else` are effect control-flow commands, not trigger clauses. For mutually exclusive trigger dispatch by a stored value, use trigger-native `switch`:

```pdx
tv_example_display_trigger = {
    switch = {
        trigger = var:tv_example_id
        0 = { always = no }
        1 = { custom_tooltip = { text = TV_EXAMPLE_REQUIREMENT has_variable = tv_example_done } }
    }
}
```

Vanilla confirms `switch` inside `common/scripted_triggers/country_triggers.txt` and numeric-variable switch keys in `events/DHE/flavor_flo.txt`. Putting an effect-style `if = { limit = { ... } ... }` chain in `common/scripted_triggers` logs `Unknown trigger type: if` and `Unknown trigger type: else_if` during load.

#### Disabled Scripted-List Examples Are Not Iterators

Do not infer a usable iterator from commented content in `common/scripted_lists`. Vanilla's `country_lists.txt` contains a fully commented `ally` example, including the comment `every_ally = {} / ... / any_ally = {}`; because the list definition itself is disabled, none of those commands is registered.

Count or inspect allies through an active country iterator plus the real alliance trigger:

```pdx
# Effect context
save_scope_as = owner
every_known_country = {
    limit = { is_allied_with = { target = scope:owner } }
    scope:owner = { change_variable = { name = ally_count add = 1 } }
}

# Trigger context
any_known_country = {
    is_allied_with = { target = root }
    relative_military_strength = { target = root value > 0.5 }
}
```

Allies necessarily know one another, so `known_country` is the bounded vanilla iterator appropriate for these checks. Direct `every_ally` and `any_ally` usage logs `Unknown effect` / `Unknown trigger type` respectively.

#### Random List Branch Filtering

Use `trigger = { ... }` inside weighted `random_list` branches when a branch should only be eligible under some condition:

```pdx
random_list = {
    1 = {
        trigger = { has_variable = candidate_a }
        set_variable = selected_a
    }
}
```

Do not use `modifier = { factor = 0 ... }` as the branch filter. Vanilla random-list examples use branch `trigger` blocks. For player-facing rerolls, exclude the current result inside the same trigger so repeated same-day clicks cannot visibly return the same option, e.g. `NOT = { var:current_demand ?= 12 }`.

#### International Organization Header Controls

The standard `organization_panel_default_header` shows the lower IO information row through `abilities_widget`, which vanilla overrides to `ios_information_header = {}`. When adding compact IO-specific status text or header action buttons, prefer the exposed `ios_information_header_content_extra_1`, `ios_information_header_content_extra_2`, or `ios_information_header_content_extra_3` blocks with `ios_header_content_extra_template`.

Do not rely on `blockoverride "country_header_extra"` for visible interactive controls in this standard IO header path. That slot sits outside the `country_government_character` / `ios_information_header` row and can be absent from the visible UI bounds or hidden behind the rendered character/header content. If replacing the whole lower row is necessary, override `abilities_widget` directly and preserve `ios_information_header` inside the replacement.

#### International Organization Custom Tab Scroll Areas

The shared organization panel's `organization_custom_content` slot is already inside an inner vbox with `margin_top = 5`, followed by an `expand` spacer. For dynamic custom tabs that can grow past the visible area, inject the `scrollarea` directly into `organization_custom_content` instead of wrapping it in another child vbox. Override the block's `margin_top`/`spacing` when the content must sit flush to the tab top. For a bounded viewport, give the scrollarea a fixed size such as `size = { 100% 430 }`; when the tab must consume the full IO pane instead of leaving the common trailing `expand` spacer to own the lower area, set the custom-content block itself to `layoutpolicy_vertical = expanding` and set the scrollarea to `using = layoutpolicy_expanding`. In both cases, let the `scrollwidget` content establish natural height with `layoutpolicy_vertical = fixed` and `ignoreinvisible = yes`. Avoid `autoresizescrollarea` for this pattern: when active state adds more cards, it can grow the viewport with the content, leaving no useful overflow and causing the scrollarea bounds to sit lower inside the wrapper. `margin_top` directly on `scrollarea` is ignored by the engine and logs an unsupported-property error.

#### International Organization Law Block Scopes

For policies under `type = international_organization` laws, scope depends on the policy sub-block. The law readme documents policy `allow` as country root, while `on_activate` / `on_deactivate` use the entity the policy applies to. In practice, IO policy execution blocks should treat the current scope as the IO when mutating IO variables or checking IO policies:

```pdx
allow = {
    international_organization_has_policy = policy:previous_level
    var:tv_alliance_cohesion >= 25
}

on_activate = {
    change_variable = { name = tv_alliance_cohesion add = -25 }
    leader_country ?= {
        change_variable = { name = tv_alliance_tier add = 1 }
    }
}
```

Do not wrap those checks/effects in `scope:recipient = { ... }` unless the specific block documents `scope:recipient`. Runtime errors such as `Undefined event target 'recipient'` and `Event target link 'scope' returned an unset scope` can be caused by generated IO policies that use `scope:recipient` inside policy `allow`, `on_activate`, or `on_deactivate`.

The policy tooltip/law browser can walk activation and deactivation effect chains before an IO has a resolvable leader country. Direct `leader_country = { ... }` can then log `Event target link 'leader_country' returned an invalid object`; use `leader_country ?= { ... }` for mirrored leader-country effects.

`scope:recipient` is documented for IO policy AI math blocks such as `wants_this_policy_bias`, `wants_propose_policy`, `wants_keep_policy`, `reasons_to_join`, and `diplomatic_capacity_cost`, where root is a country and recipient is the IO. In custom non-unique IO laws, the engine can still pre-evaluate these maths without a recipient event target. Guard direct recipient reads with `exists = scope:recipient` in the same `limit` block, or use optional `scope:recipient ?= { ... }` for trigger-only checks, before reading `scope:recipient.leader_country` or IO variables.

Vanilla policy votes add automatic modifier utility to each voting country's support calculation:
`scope:vote.modifier_utility(scope:actor)` is displayed as `POLICY_MODIFIER_UTILITY` and multiplied in `policy_vote`. For visible IO law effects that are intended only for the leader country and must stack with other law modifiers, keep them as additive `country_modifier` blocks but make the display filter recipient-safe: `country_modifier = { potential_trigger = { OR = { NOT = { exists = scope:recipient } is_leader_of_international_organization = scope:recipient } } ... }`. Ordinary law-browser tooltips can lack the vote recipient event target, so the no-recipient branch keeps the effect visible; when recipient exists, the leader check still prevents non-target members from receiving or valuing the modifier package as their own direct benefit. Use `leader_modifier = { ... }` only when its documented replacement behavior is intended.

`generic_action_ai_lists` potentials use the evaluating country as root. Inside `any_international_organizations_member_of`, `this` is the iterated IO, so `leader_country = this` compares a country to an international organization and logs a type-mismatch error. Use `exists = leader_country` plus `leader_country = root` for leader-only action lists.

#### International Organization Law Votes and Special Status Power

For an IO law system that routes policy changes through the parliament UI, the parliament type and the laws are only part of the setup. `requires_vote = yes` on the law and `uses_parliament_for_law_votes = yes` on the parliament type start the policy vote flow, but vote eligibility is driven by special status power.

Create an entry under `common/international_organization_special_statuses`, list that status in the IO type's `special_statuses_implemented`, give the status a `special_status_power`, and enable a matching `<status>_can_participate_in_parliament = yes` modifier in the IO parliament type. For any custom IO special status that can be implemented by an IO, define both `<status>_can_participate_in_parliament` as boolean and `<status>_agenda_impact` as percent in `main_menu/common/modifier_type_definitions` with `game_data = { category = internationalorganization }`; missing either name can log startup DB assertions.

For custom IO statuses that drive parliament voting or visible special-status power, do not rely only on `auto_bestowal_trigger`. Follow the HRE free-city pattern at the lifecycle point that changes membership or rank: directly add or remove the special status from the IO scope. Do not add recurring monthly refreshes for special-status display repair, and do not add full-member or parliament-seat repair unless a separate runtime error proves it is needed.

Vanilla `policy_vote` checks `country_combined_special_status_power(scope:recipient) > 0` for IOs using parliament law votes. If no implemented special status supplies voting power, a law debate may begin but the IO parliament page has no voter group to display.

The same vanilla law-vote path calls `call_parliament_for_law_change`, which must resolve a meeting location before it activates the IO parliament issue. For non-HRE IOs the lookup order is: `parliament_seat`, then a proposer-owned location that is owned by the IO, then a random IO-owned location. If a custom IO has no IO-owned locations, set the IO variable `parliament_seat` to a valid location such as the leader country's capital before policy votes can be proposed; otherwise `set_parliament_location` can receive a null target.

Custom IO parliament sessions also need at least one valid `common/parliament_agendas` entry for the participating special status. Define it with `type = international_organization` and `special_status = <status>`, with `potential`/`allow` that pass for the IO. Otherwise the parliament UI can report that no special status wants to propose an issue even when valid `parliament_issues` exist.

For player-callable idle IO parliament sessions, also ensure at least one normal issue for the participating special status is positively desired in ordinary states. The vanilla `call_organization_parliament` action builds its chooser from `every_possible_parliament_issue`; if all custom issues have non-positive `wants_this_parliament_issue_bias` after their normal base and modifiers, the picker can report that no special status has any issue to bring even when `potential`, `allow`, and `selectable_for` pass.

For single-member or founder-only IOs, do not use the vanilla `call_organization_parliament` issue picker for support-token meetings. Even with a leader/founder special status, the picker can still report that no special status wants to propose an issue, and `propose_parliament_issue` initializes support from the issue special status before marking the proposer as voting yes. Redesign the mechanic before enabling custom support meetings for a founder-only IO.

The shared IO panel does not expose a real `organization_parliament_tab_visible` override block. In `panels/organization/common.gui`, the parliament tab's `visible` property is bound directly to `InternationalOrganizationsView.GetInternationalOrganization.HasParliament`. To hide the parliament tab for an IO, set `has_parliament = no` on the IO type. Law `requires_vote` behavior is separate and should follow the mechanic's design.

### 4.4. Common File Types and Formats

Modders primarily work with a few text-based file formats:

| Extension | Purpose                                  | Notes                                       |
| --------- | ---------------------------------------- | ------------------------------------------- |
| `.json`   | Metadata                                 | Used for `metadata.json`.                   |
| `.txt`    | Game Scripts (Events, Decisions, etc.)   | The primary format for scripting game logic.  |
| `.yml`    | Localization                             | Must be saved with **UTF-8-BOM** encoding.  |
| `.gui`    | User Interface Layouts                   | Defines the structure and look of UI windows. |

#### Localization Key Uniqueness

Within each `main_menu/localization/<language>/` tree, every localization key must be defined exactly once. Duplicate YAML keys across files do not merge: startup logs a `Duplicate localization key` error and one source silently shadows the other. When a generated localization file takes ownership of a key family, remove the stale manual copies instead of keeping both definitions.

### 4.5. Observed Best Practices

The community analysis highlighted several best practices for creating clean, compatible, and maintainable mods:

*   **Avoid Overwriting Vanilla Files**: Instead of editing game files directly, create new files with unique names. This prevents conflicts with other mods and game updates.
*   **Use Prefixes**: Prefixing filenames with a unique identifier (e.g., `my_mod_events.txt`) helps organize files and prevent name collisions.
*   **Isolate Content**: Keep all mod files within the mod's designated folder. Do not place files in the main game directory.
*   **Manage Load Order**: For files that must override others, use numbered prefixes (e.g., `00_`, `01_`) to control the order in which the game loads them.
*   **Use Version Control**: Employ tools like Git to track changes, collaborate with others, and revert to previous versions if needed.

## 5. Core Modding Concepts

EU5's scripting language revolves around a few core concepts: Triggers, Effects, and Scopes.

### 5.1. Triggers and Effects

*   **Triggers** are conditions that check the current game state. They are used to determine if an event can fire, an option is visible, or a decision can be taken. Triggers return a boolean value (true or false). [4]
*   **Effects** are commands that change the game state. They are used to apply modifiers, change country ownership, create characters, and more. [5]

Both triggers and effects can be *inline* (for simple operations) or *block* (for more complex logic) and are highly dependent on the current **scope**.

#### `construct_building` Cost Multipliers

When `construct_building` uses `cost_multiplier`, EU5 requires a localized reason key:

```pdx
construct_building = {
    building_type = building_type:theater
    instant = yes
    cost_multiplier = 0
    cost_multiplier_reason = "game_concept_event"
}
```

Omitting `cost_multiplier_reason` logs: `No reason given for the cost multiplier in construct_building effect`. Vanilla event-funded construction commonly uses `game_concept_event`, which is already localized.

When a player-facing event option starts normal building construction, prefer a visible
`construct_building` / `change_building_level_in_location` effect in that option. The engine
renders the building name, price, and cost modifiers from the effect tooltip. Do not duplicate
that with option text like "Spend 400 ducats" plus hidden `pay_price` and free construction
unless the flow is intentionally event-funded, nonstandard, or hidden.

#### Scripted Trigger Parameters That Add Type Prefixes

When a scripted trigger template adds a type prefix around a parameter, pass the bare database id to that parameter. For example, vanilla `location_and_owner_can_build` expands its argument as `building_type:$building_type$`, so the call must be:

```pdx
location_and_owner_can_build = { building_type = theater }
```

Do not pass `building_type:theater` to that helper. It expands to `building_type:building_type:theater` and logs `More than one colon in event target link`.

#### `construct_building instant = yes` Is Not Synchronous Level Sync

Treat `construct_building = { ... instant = yes }` as a queued 0-day construction task, not as an immediate `location_building_level` update. Do not write `while` loops that wait for `location_building_level` to change inside the same effect after `construct_building instant = yes`, and do not leave old-save reconstruction logic on hot click paths that fire from wonder site selection or similar actions.

If a scripted effect must bring a building to a stored target level, compute the missing levels from persistent state and apply one bounded `change_building_level_in_location` delta, or branch over fixed thresholds with `if` / `else_if`. The effect body should run once and finish without depending on same-effect building-level refresh.

#### Dynamic Event Gold Costs

For country event options that should scale with the country's economy, vanilla uses:

```pdx
change_gold_effect = { scale = -3.5 }
```

The helper wraps `add_gold` and scales the value with `capital_wealth` and `country_economical_base`, with clamps for positive and negative results. Use fixed `add_gold = -N` only when a flat cost is the design intent. Example: vanilla `laws.0005` offers a free `research_progress_weak_bonus` (+2.5) option and a paid `change_gold_effect = { scale = -3.5 }` + `research_progress_severe_bonus` (+10) option.

#### Price Definitions and Cost Modifiers

Mod-defined prices in `in_game/common/prices/` are not complete by themselves. For each price key, EU5 looks for a matching modifier type named `<price_key>_cost_modifier`.

```pdx
my_action_price = {
    scaled_gold = 3.5
}

my_action_price_cost_modifier = {
    color = bad
    percent = yes
    game_data = {
        category = country
    }
}
```

Define the modifier type in `main_menu/common/modifier_type_definitions/`, and localize all three keys in every supported language: `my_action_price`, `MODIFIER_TYPE_NAME_my_action_price_cost_modifier`, and `MODIFIER_TYPE_DESC_my_action_price_cost_modifier`. If the modifier type is missing, the engine logs `Missing modifier type for price. <price_key>_cost_modifier`.

#### v1.3 Built-in Modifier Rename: `_cost` -> `_efficiency`

Separate from the mod-defined `<price_key>_cost_modifier` convention above, EU5 v1.3 renamed
roughly 29 pre-existing built-in static modifiers from a `_cost`/`_cost_modifier` suffix to an
`_efficiency` suffix (e.g. `global_build_buildings_cost` -> `global_build_buildings_efficiency`,
`fort_maintenance_cost` -> `fort_maintenance_efficiency`, `army_reinforce_cost` ->
`army_reinforce_efficiency`, `global_bureaucracy_maintenance_cost_modifier` ->
`global_bureaucracy_maintenance_efficiency`). Two names don't just gain the suffix:
`stability_cost` -> `stability_cost_efficiency` and `court_spending_cost_modifier` ->
`court_spending_efficiency`.

The rename also flips `color = bad` to `color = good`, so every occurrence's value must be
negated, not just renamed. Confirm via `git diff` on
`main_menu/common/static_modifiers/00_modifier_types.txt` between reference commits before and
after a version bump — do not assume a fixed multiplier applies uniformly; Paradox sometimes
rebalances a field's magnitude at the same time as the rename (verify via a same-named
`country_modifier`/`static_modifier` block that exists in both versions where possible). See
`docs/knowledge/anti_patterns.yaml` rule `v1_3_cost_modifier_renamed_to_efficiency` and
`docs/knowledge/risk_cards/wonders.md` rule 16 for the concrete list this project hit.

#### Modifier Type Icons

Modifier type definitions do not define their own UI icons. EU5 loads modifier icon mappings from `main_menu/common/modifier_icons/*.txt`. Any mod-defined modifier type that can appear in UI should have a same-key icon mapping:

```pdx
my_action_price_cost_modifier = {
    positive = "gfx/interface/icons/modifier_types/hire_advisor_cost_modifier.dds"
}
```

Use vanilla DDS paths directly when a close icon already exists. If the mapping is missing, startup logs `Missing Icon for Modifier : <modifier_type_key>` even though the modifier type itself is valid.

#### Character Static Modifiers for Commander Effects

Character-scoped static modifiers can carry military leader effects. Vanilla examples include `general_mil` with `discipline` and `army_movement_speed`, and `horde_battle_plans` with `military_tactics` and `army_movement_speed`. General traits also use the same modifier types.

For an effect that should follow a specific appointed commander, define the static modifier with character game data and apply it in character scope:

```pdx
my_general_tactic = {
    game_data = {
        category = character
    }
    discipline = 0.05
    army_movement_speed = 0.10
}

var:my_general_char ?= {
    add_character_modifier = { modifier = my_general_tactic years = -1 mode = replace }
}
```

Use a country modifier only when the design intentionally grants the bonus country-wide and independently of the active commander.

Governor's House War Tent tactics are a documented exception. Their stored-general character modifier path did not make the combat bonuses take effect, so the feature intentionally applies `tv_govhouse_tactic_*` as country-scoped modifiers and comments that this is a gameplay approximation. Do not convert that specific system back to `add_character_modifier` unless a new active-commander implementation is verified at runtime.

#### Goods Production and Trade Quantity Metrics

Custom goods should use their own named color key. Reusing a vanilla goods color such as `color = goods_masonry` can load, but the engine logs:

```text
Goods <custom_good> has same color as <vanilla_good>
```

Define a unique color in `src/main_menu/common/named_colors/` and reference that key from the goods definition, for example `color = goods_tv_wonder_materials`.

Use the goods-specific world trigger value when a mechanic needs actual global output for one good:

```pdx
set_variable = { name = my_world_horses value = "produced_in_world:horses" }
```

Do not use `total_effective_goods_production_buildings(goods:<good>)` for this purpose. That country-scope function measures effective building levels that produce the good, not the world goods quantity.

For a country's own trade in a good, iterate its trade objects and read `trade_volume`:

```pdx
set_local_variable = { name = member_trade_total value = 0 }
every_trade = {
    limit = { goods = goods:horses }
    change_local_variable = { name = member_trade_total add = trade_volume }
}
# Read local_var:member_trade_total here, then clean the scratch value.
remove_local_variable = member_trade_total
```

For IO member trade totals, wrap the same trade-object loop in `every_international_organization_member`. Avoid summing `traded_in_market:<good>` from `every_market_present_in_country` when the design asks for member-owned trade; `traded_in_market:<good>` is the whole market's traded quantity and shared markets can be counted once per member.

When a mechanic needs market route control rather than a country's own trade, iterate the market's route groups and read `trade_volume` from the export/import entries. This is the required pattern for Trade League monopoly control: origin and node slots use market `every_export` routes filtered by `goods = goods:<good>`, while consumer slots use market `every_import` routes. `produced_in_market:<good>` and `goods_demand_in_market(goods:<good>)` are useful ranking inputs for origin and consumer markets, but `traded_in_market:<good>` and `goods_supply_in_market` are not reliable route-volume proxies.

When the mechanic genuinely needs to handle all goods from an export/import route, avoid generating one route scan per good. Route scopes expose the traded good scope:

```pdx
every_export = {
    limit = { to_market = scope:target_market }
    traded_goods = { save_scope_as = route_good }
    # scope:route_good can be used as a variable_map key.
}
```

Vanilla also uses `goods = scope:target_goods` for effects such as `add_goods_supply`, but `add_temporary_demand` has only verified static `type = demand:<id>` examples; keep a static demand-type dispatch unless a dynamic demand type is separately verified.

### 5.2. Scopes and Scope Links

A **scope** refers to the specific game object (e.g., a country, a character, a location) that a script is currently focused on. **Scope links** are used to access data from or apply effects to other scopes. For example, `c:FRA.gold` would access the treasury of the country with the tag FRA.

#### Variable Maps

Source authority: this subsection preserves the user-provided Variable maps reference excerpt [14] plus TV runtime tests from 2026-06-04. Treat [14] as the local authoritative source for variable-map basics because official defines and vanilla references currently expose very little `variable_map` detail.

Variable maps are associative arrays: one key scope or number maps to one value scope or number. They follow the same three-storage pattern as variables and variable lists:

| Type | Stored on a scope | Persistent | Add effect | Scope link |
|---|---|---|---|---|
| regular | yes | yes | `add_to_variable_map` | `"variable_map(name|key)"` |
| global | no | yes | `add_to_global_variable_map` | `"global_variable_map(name|key)"` |
| local | no | no | `add_to_local_variable_map` | `"local_variable_map(name|key)"` |

Add entries with `name`, `key`, and `value`. The key and value can be game scopes such as countries, locations, buildings, or characters; integer keys also work, so a map can act like a sparse indexed array.

```pdx
add_to_variable_map = {
    name = rival_map
    key = c:FRA
    value = c:ENG
}
```

Adding an already existing key does not overwrite the value; the add effect silently keeps the old entry. To update a mapping, remove the key first and then re-add it:

```pdx
remove_from_variable_map = {
    name = rival_map
    key = c:FRA
}
add_to_variable_map = {
    name = rival_map
    key = c:FRA
    value = c:SPA
}
```

The normal and safest use of a variable-map lookup is as a quoted scope link on the left side, entering the saved value scope:

```pdx
"variable_map(rival_map|c:FRA)" = {
    # this is c:ENG; prev is the caller scope
    add_prestige = -10
}
```

The quoted expression takes the map name before `|` and the key expression after it. Because the expression is quoted, scripted effect/trigger arguments are not expanded inside it. Save a dynamic key to a variable first:

```pdx
set_local_variable = {
    name = temp_key
    value = $key$
}
"global_variable_map(my_map|local_var:temp_key)" = {
    # Work with the mapped value scope here.
}
```

Only the key can be made dynamic this way. The map name is an identifier, not a scope or value expression, so `"global_variable_map($map$|c:ENG)"` and `"global_variable_map(local_var:map_name|c:ENG)"` should be treated as invalid.

Global-root on_action callbacks are not variable-owning scopes. If a reachable branch in that root
needs a no-op effect body, use global storage effects (`set_global_variable` followed by
`remove_global_variable` on a scratch name) or enter a variable-owning scope first; a bare
`remove_variable` at that root logs "This scope does not have variables."

TV runtime tests found an important limitation: although some references describe direct numeric extraction from `"variable_map(name|key)"`, treat direct right-hand-side use as unreliable in this project. Variable-map scope links are reliable for entering the mapped scope on the left side, but can fail or compare as the wrong type when used directly as an equality RHS, trigger RHS, or effect parameter after scope changes.

Do not write:

```pdx
set_local_variable = { name = probe_key value = 1 }
var:tv_wonder_site ?= {
    every_buildings_in_location = {
        limit = {
            building_type = "variable_map(tv_wonder_probe_helper_by_wonder_id|local_var:probe_key)"
        }
        location = { destroy_building = prev }
    }
}
```

Instead, capture the mapped value before entering the later scope, then use the captured variable as the RHS. Prefer `set_local_variable` for temporary use unless a persistent scoped variable is actually needed:

```pdx
set_local_variable = { name = probe_key value = 1 }
set_local_variable = {
    name = helper_building_type
    value = "variable_map(tv_wonder_probe_helper_by_wonder_id|local_var:probe_key)"
}
var:tv_wonder_site ?= {
    every_buildings_in_location = {
        limit = {
            building_type = local_var:helper_building_type
        }
        location = { destroy_building = prev }
    }
}
```

This direction is valid: `set_local_variable` is performed before entering the later
`var:X ?= {}` / location scope, and `local_var:helper_building_type` is read inside that
nested scope. Do not confuse it with the separate bad pattern where a local variable is
created inside a dynamic scope and then read outward through `prev = {}` or after leaving
that scope.

Runtime tests from 2026-06-05 narrowed this limitation for event-option building tooltips:
dynamic building effects themselves can render. `construct_building = { building_type =
local_var:X ... }` and `change_building_level_in_location = { building = local_var:X value =
-N ... }` both rendered in `tv_engineering_department.200` / `.201` when `X` was captured
from a `global_variable_map` lookup keyed directly by persistent project state such as
`var:tv_wonder_locked`. The failing module-construction chain computed a composite key
(`tv_wonder_locked * 10 + tv_wonder_last_completed_part`) with `set_variable` /
`change_variable` earlier in the same visible option chain, then immediately used that key
for the map lookup. Treat that as an event-tooltip pre-render dependency failure, not as
proof that `building_type = local_var:X` or dynamic `change_building_level_in_location`
cannot render. The safe pattern is to branch over a bounded non-wonder dimension, such as
the four module parts, and use a direct map keyed by already-existing wonder state.

If the mapped value needs to persist on the current scope, use `set_variable = { name = X value = "variable_map(...)" }` first, then read `var:X` from that same owning scope or capture it into a local variable before switching scopes.

Do not compensate for missing variable-map data by rebuilding maps from read paths. Global
map indexes belong to lifecycle effects: startup, save-load initialization,
data-change regeneration, and explicit initialization. GUI refresh, country cache refresh,
tooltip/projection effects, selection handlers, and monthly readers are hot paths; adding
`*_rebuild_*_maps*_effect` calls there, including `*_if_needed` rebuild routers, hides
ordering bugs and makes every read pay for a global compatibility check. Performance is a
project priority, so do not spend hot-path work on obsolete internal states. If a cache read
sees an uninitialized map, fix the current
lifecycle hook or move the dependent state write earlier so the existing refresh condition
is true; do not add old-schema repair or preserve abandoned internal states.

Variable maps can be iterated over their keys. Use `every_key_in_variable_map` or `ordered_key_in_variable_map` as effects, and `any_key_in_variable_map` as a trigger; use the `global_` and `local_` variants for global/local maps. Inside a key iterator, `this` is the current key. Enter the mapped value through the scope link:

```pdx
every_key_in_variable_map = {
    variable = rival_map
    "variable_map(rival_map|this)" = {
        # this is the mapped value; prev is the key
    }
}
```

`ordered_key_in_variable_map` selects only one key by default. Add `max = N` when multiple keys should be processed, but do not use an inflated number as an "all keys" shortcut. Runtime testing showed the engine logs a Script system error when `max` is larger than the current key list, even though it caps the value internally. Use `every_key_in_variable_map` plus a found flag when the current count is not known.

When a key iterator reads sibling maps stored on the original country/scope, do not run
`is_key_in_variable_map` directly from the callback scope. Runtime testing showed the callback
scope can be the numeric key itself, which logs "This scope doesn't support variables" for
country-scoped map checks such as `target = this`. Save the map owner before the iterator,
copy `this` into a local variable inside the callback, then perform the sibling map checks under
`scope:<saved_owner>` with `target = local_var:<key>`.

The same owner-scope rule applies to ordinary item iterators over country-owned variable lists.
`every_in_list`, `random_in_list`, and `any_in_list` switch the current scope to the list item,
so a list of regions, locations, or characters is not the country scope that owns the map. Copy
the region/location/character key into a local variable, then enter the saved country scope for
both `is_key_in_variable_map` and the quoted `variable_map(...)` scope link.

When a variable-map key callback is reached from a generic action effect or selector tooltip,
do not assume `root` is a valid country event target. Save the current country before entering
the callback, then write through the named scope:

```pdx
save_scope_as = proposal_owner
random_key_in_variable_map = {
    variable = feasible_deck
    scope:proposal_owner = {
        set_variable = { name = selected_id value = prev }
    }
}
```

This preserves the variable-map key stream while avoiding `Event target link 'root' returned an
unset scope` during hover pre-evaluation.

GUI has separate variable-map data functions. Use `Scope.GetMapKeys('<name>')` and `GetGlobalMapKeys('<name>')` for key datamodels, and `Scope.GetVariableFromVariableMap('<name>', Scope)` / `GetVariableFromGlobalVariableMap('<name>', Scope)` to retrieve values from a typed GUI scope. GUI string recovery has its own traps; do not use `GetFlagName` from variable-map values as a raw script key.

Variable maps are unordered. Their internal iteration order is stable but not insertion order; sort with ordered key iterators when order matters. They are useful when many scopes need key-based lookup, when a map substitutes for variables on scopes that cannot store variables directly, or when an indexed array-like structure is clearer than hundreds of generated branches.

#### `root` vs `prev` in reusable country triggers

Do not assume `root` is the country just because a scripted trigger is country-scoped. `root` stays the root scope of the caller. If a country trigger is called from a situation `every_country` block, the current country is `this`, but `root` can still be the situation.

Inside nested iterators such as `any_market_with_merchants`, use `prev` to refer back to the country being checked. This matters for target triggers such as:

```pdx
any_market_with_merchants = {
    most_powerful_merchant = prev
    count >= 5
}
```

The GUI can hide this bug: `ShowTriggerConditions('trigger_name', PlayerScope.Self)` evaluates with the player country as root, while the monthly situation checker may evaluate the same trigger with situation root. A milestone can therefore show all conditions green in the panel but never grant the node unless nested country references use `prev` or an explicit saved scope.

#### Nullable links in broad location iterators

`any_location_in_the_world` and geography iterators can include water, non-ownable locations,
and ownable locations with no owner. A direct `owner = <country>` or
`dominant_culture = <culture>` link dereferences the current location's object and can therefore
log an invalid-object error during generic-action tooltip pre-evaluation. Saving the country
scope protects the comparison's right-hand side, but does not make the iterated location's
nullable link valid.

Filter the iterator and use optional links. This checks that every ownable location matching a
country's culture is directly owned, while treating an ownerless matching location as not owned:

```pdx
save_temporary_scope_as = task_owner
NOT = {
    any_location_in_the_world = {
        is_ownable = yes
        dominant_culture ?= scope:task_owner.culture
        NOT = { owner ?= scope:task_owner }
    }
}
```

For a pure geographic unification check, omit the culture line but retain
`is_ownable = yes` and `NOT = { owner ?= scope:task_owner }`. The optional
`dominant_culture ?=` link safely excludes locations without a culture object; the optional owner
link safely returns false for an ownerless location, making the enclosing `NOT` succeed.

### 5.3. Script Values

Script values are used for mathematical calculations and creating dynamic numerical values. They can be defined as reusable named values in the `common/script_values/` folder or created inline within other scripts. They support a wide range of arithmetic and logical operators. [6]

#### Dynamic Numeric Values From Selectors

When a generic action value selector, scope link, or variable chain provides a number that will be stored or passed into a numeric effect parameter, wrap it in an explicit script-value block:

```pdx
set_variable = { name = my_used_pct value = { value = scope:target_1 } }
set_variable = { name = my_amount value = { value = scope:target_1 divide = 2 } }

add_temporary_demand = {
    type = demand:my_virtual_demand
    scale = { value = scope:my_io.var:my_amount }
    months = 2
}

add_goods_supply = {
    goods = goods:horses
    amount = { value = scope:my_io.var:my_amount }
}
```

Do not pass these dynamic values directly as `value = scope:target_1`, `scale = scope:X.var:Y`, or `amount = scope:X.var:Y`. Runtime behavior in the Trade League virtual demand/supply actions showed those direct forms can collapse to `1`, regardless of the selected percentage. The script-value block preserves the numeric value and is also where inline arithmetic such as `divide = 2` belongs.

#### Scope Navigation in Script Values — `location.` prefix rule

Script values always execute in the scope they are *called from*, not from the scope implied by their name prefix. The `location.` prefix is a **scope navigation link** that transitions from an outer scope (pop, character, market, etc.) *to* a location. This means:

- **Correct — pop-scope value calling a location-scope value:**
  ```
  sol_alcohol_demand_scale = {   # runs in pop scope
      add = location.local_nobles_alcohol_demand_scale   # navigate to location
  }
  ```
- **Correct — location-scope value referencing other location variables:**
  ```
  local_nobles_alcohol_demand_scale = {   # runs in location scope
      value = local_nobles_savings_pressure   # already in location scope — no prefix
      multiply = local_noble_gdp_per_capita_display
  }
  ```
- **WRONG — using `location.` inside a location-scope value:**
  ```
  local_nobles_alcohol_demand_scale = {
      value = location.local_nobles_savings_pressure   # ERROR: already in location scope
  }
  ```
  Engine error: `Event target link 'location' did not get a matching scope type. Expected 'character, pop, …', but got 'location'`

#### Function-Call-Style Event Target Links Must Be Quoted

Some event target links take a parenthesized argument instead of a colon suffix, e.g. `estate_power(estate_type:crown_estate)` or `estate(estate_type:nobles_estate)`. When one of these is chained after a scope and used as the RHS of `value =`, a trigger comparison, `add =`, `subtract =`, etc., the **entire scope + call expression must be wrapped in double quotes**:

```pdx
value = "leader_country.estate_power(estate_type:crown_estate)"
```

```pdx
limit = { "root.estate_power(estate_type:crown_estate)" >= 0.5 }
```

`building_efficiency` also has this numeric form even though it is documented in
`triggers.log` as a location-scoped threshold trigger. Use the same quoted
parenthesized style for numeric reads:

```pdx
value = "var:tv_wonder_site.building_efficiency(building_type:tv_wonder_labor_camp)"
```

In-game validation of the Engineering Department wonder worksite showed this value tracks
labor/staffing satisfaction, matching the meaning of `total_effective_building_levels:X`
relative to nominal completed levels. Do not use `building_efficiency` as the material/input-goods
green bar. The green bar is GUI `Building.GetInputGoodsAccess`; no matching script numeric
event target was found in official defines. In script, use building-scope `is_lacking_goods` as
the boolean gate for whether the building is actually short of inputs; small market imbalances can
leave the building's input percentage untouched. Do not treat `building_goods_input(goods:<input>)`
as that green bar: reference mod 3735059838 uses it as a required-input value scaled by market
access and `building_efficiency`, so it is entangled with the labor side. If a script-side numeric
material-satisfaction approximation is needed after `is_lacking_goods` is true, compute the
relevant market-scope supply/demand ratio for each required input, such as
`goods_supply_in_market(goods:<input>) / goods_demand_in_market(goods:<input>)`, cap each ratio
to 0..1, and average the ratios across the fixed input list. For a two-input recipe, if only one
input is short by x%, the material/input penalty is x/2%.

From a building scope, reference mod 3735059838 uses:

```pdx
value = "location.building_efficiency(scope:epbm_bt)"
```

Without quotes, the parser splits on the bare `(` and fails with a cluster of three errors: `jomini_eventtarget.cpp: No data specified for an event target link that requires data`, `jomini_scriptvalue.h: Cannot read [...] as a script value`, and `pdx_persistent_reader.cpp: Unexpected token: (` (immediately followed by `Unexpected token: )` and `Unexpected token: =` on the next lines). This differs from plain colon-suffixed links (`var:X`, `estate:crown_estate`), which never need quoting. See `reference_game_files/game/in_game/common/disasters/coup_attempt.txt:13`, `reference_game_files/game/in_game/common/attribute_columns/57_parliament_issues.txt:40`, `reference_game_files/game/in_game/events/estates/burghers_estate_events.txt:144-145`, and `reference_game_files/game/in_game/events/government/D008_latinization_vs_hellenization.txt:2593` for verified vanilla precedent.

### 5.4. Generic Action `select_trigger` Pre-evaluation

When a generic action has multiple `select_trigger` steps, EU5 **pre-evaluates the `effect` block at each step** before the user finishes all selections:

- After step 1 completes, the first `target_flag` scope (e.g. `scope:target`) is set but subsequent ones (`scope:target_1`) are not.
- At step 2 display time, the engine may evaluate the effect with `scope:target` set to the selected character — but any variables that the effect itself would write (e.g. `tv_governed_region`) do not yet exist on that character.

Wrapping the action effect in `hidden_effect` does not stop this selector pre-evaluation. It
hides effect text, but the pre-evaluator can still walk into nested `scripted_effect` calls.
Any helper reached from a generic action must not assume variables written earlier in that same
effect chain exist during hover.

For display-refresh helpers that derive a row, timeline, or progress state, do not write a
persistent variable and then immediately compare `var:X` later in the same chain. Compute the
derived values with `set_local_variable` / `change_local_variable`, compare `local_var:X`, and
only then mirror the final values into persistent variables for GUI display. This avoids
`Failed to fetch variable` / `Invalid left side during comparison 'var'` errors when a generic
action's selector or tooltip pre-evaluator walks the effect before same-chain `set_variable`
writes have been committed.

Reusable helpers reached from generic actions should also avoid assuming `root` is the current
country after they enter nested IO/member iterators. If the helper needs to compare nested state
to the action actor or current country, save that owner at helper entry with `save_scope_as =
<owner_scope>` and compare against `scope:<owner_scope>` instead of `root`.

The same caller-sensitive-root rule applies to scripted triggers reached from a generic-action
effect chain. A trigger such as `any_location_in_the_world = { owner = root }` can be valid from
one caller and emit `Invalid right side during comparison 'root'` when action-tooltip
pre-evaluation reaches it. At the country-scope entry of such a trigger, use
`save_temporary_scope_as = <owner_scope>` and then compare nested scopes to
`scope:<owner_scope>`; use `scope:<owner_scope>.culture` for country culture links. Do not use
`save_scope_as` in a trigger context.

Cleanup-only helpers are still different from player-facing effects: if the button is only
clearing variables, removing list entries, stripping stale modifiers, or rebuilding display
state, call that helper from `hidden_effect = { ... }` so the cleanup is not rendered as tooltip
content. `scripts/validate.py` keeps a registered hidden-only helper list for recurring traps
such as `tv_governor_remove_effect`.

**Required guards:**

1. Wrap the entire effect body in an existence check for all required named scopes:
   ```
   if = {
       limit = {
           exists = scope:target
           exists = scope:target_1
       }
       # ... actual effect body
   }
   ```
2. Within scripted effects called by the action effect, use `?=` on any variable access that may be absent on a freshly selected character:
   ```
   var:tv_governed_region ?= {   # silently skipped if character has no tv_governed_region yet
       every_location_in_region = { ... }
   }
   ```

The `exists = scope:<name>` trigger is the vanilla pattern for this (confirmed in `assign_governor.txt` and `assume_fort_command.txt`). The errors appear in `error.log` as "Undefined event target" or "Failed to fetch variable" but the effect still fires correctly once all selections are complete.

`save_scope_as` is an effect only; it is not registered as a trigger type at all. Any scope save
performed inside a `select_trigger` `visible`/`enabled` block, an `allow`/`potential` block, or an
`if = { limit = { ... } }` trigger body must use `save_temporary_scope_as` instead. Using
`save_scope_as` in a trigger context logs `Unknown trigger type: save_scope_as` at load time, once
per occurrence — a single reused generator helper can produce hundreds of duplicate errors. Confirmed
against vanilla `coa_def_BOH_ensign_trigger` (`c:BOH = { save_temporary_scope_as = custom_overlord }`
inside a trigger-only `scripted_trigger` block). Reserve `save_scope_as` for saves written directly
inside an effect body (a sibling of `limit`, not inside it).

Temporary and permanent scope target names share one namespace: do not reuse the same name for a
`limit`-context `save_temporary_scope_as` and a later real `save_scope_as` in the same effect chain
(e.g. an `every_in_list = { limit = { save_temporary_scope_as = tv_display_region ... } save_scope_as
= tv_display_region ... } }` loop). The engine logs `Trying to add the temporary target '<name>'
which has the same name as a permanent target` and the effect silently fails at runtime — this
reproduced as a broken "appoint regional governor" action in
`tv_govhouse_refresh_governor_display_effect` (`tv_govhouse_effects.txt`). Give the trigger-context
temporary save a distinct name (this project's convention is `<name>_check`), keeping the real
`save_scope_as = <name>` for the effect body outside `limit`.

Do not mirror target availability in the action `allow` block just to avoid an empty chooser.
The `select_trigger` definition already supports `none_available_msg_key`, documented by
vanilla as the localization shown when no targets are available. Put target eligibility in
the selector's `visible` / `enabled` blocks, let the chooser report the empty-target state,
and keep `allow` for actor, state, cost, or phase prerequisites. An `allow` trigger that scans
for "any valid target" performs the same expensive candidate search before the selector does
its own pass during rendering, tooltip, and AI/list evaluation.

If a later selector filters on a previous selection, keep it in the same interaction-target
chooser. A later `select_trigger` with `source = world` can lose access to earlier flags such
as `scope:target`; when its `visible`/`enabled` block asks for that flag, the engine can show
an empty chooser and log `Asking for a flag that's not in the interaction target chooser
specified`. Omit `source = world`, use a non-world source, or build an `interaction_source_list`
when the selector depends on earlier selections.

For player-facing custom candidate lists, use `interaction_source_list`, not
`ai_interaction_source_list`. The official type note defines `ai_interaction_source_list` as the
same mechanism applied only to AI countries. If it is the only custom list, human players can see
the selector's `none_available_msg_key` even when the target exists; reserve the `ai_` form for an
AI override after the player selector has its own `source`, `source_flags`, or
`interaction_source_list`.

#### Character-menu actions are `character_interactions`, not Generic Action `type = character`

In the current engine build, `common/generic_actions` rejects `type = character` with
`Failed to read enum! Type: "EGenericActionType", Val "character"`. Do not rely on the stale
generic-actions readme comment that lists that value. An action that belongs in a character's
lateral-view or right-click menu must instead be defined under
`common/character_interactions/`, following vanilla `appoint_dragoman.txt`:

```pdx
tv_example_appoint_character = {
	message = yes
	on_own_nation = yes
	potential = { scope:actor = { has_variable = tv_feature_initialized } }
	allow = { scope:actor = { always = yes } }
	select_trigger = {
		looking_for_a = character
		source = actor
		target_flag = recipient
		visible = { is_alive = yes }
	}
	effect = { scope:actor = { tv_example_appoint_effect = yes } }
}
```

Character-interaction registration does not itself populate `scope:recipient`: the selector's
`target_flag = recipient` does. Put target eligibility in that selector and guard its effects with
`exists = scope:recipient`. Provide the standard character-interaction localization keys `<id>`,
`<id>_concept`, `<id>_act`, `<id>_desc`, `<id>_desc_specific`, `<id>_past`, and `<id>_act_past`.
These are not generic actions: do not add them to `generic_action_ai_lists` or generate
`PERFORM_<id>_ACTION` message types.

#### Generic Action AI Lists

Every generic action should be explicitly listed in `in_game/common/generic_action_ai_lists/`. Vanilla's readme says unlisted actions are put into the global list, and EU5 logs a performance warning such as `Action X is not explicitly listed in an ai list!`.

Use the AI list `potential` block to restrict evaluation to countries that can use the feature. Player-facing actions should still be listed; set restrictive AI behavior such as `ai_will_do = { add = -100 }` when the AI should never execute them.

When AI should use a simple situation/generic action, prefer action-native AI (`ai_tick`,
`ai_tick_frequency`, `ai_will_do`, and the AI list entry) over a monthly/on_action helper that
duplicates the action's select/effect flow. Broad pulses do not automatically have the literal
`scope:actor` event target that generic actions and building `allow` blocks expect. A copied AI
helper that calls `location_and_owner_can_build` or `can_build_building` can therefore evaluate a
building's `allow = { scope:actor = { ... } }` block with no actor target and spam
`Undefined event target 'actor'` / unset-scope errors.

#### Generic Action Message Types

Generic actions also need notification message types in `main_menu/gui/messagetypes.txt`. This project keeps those entries in `scripts/gen_messagetypes.py`; after adding a new generic action, add a `PERFORM_<action_id>_ACTION` block there and rerun the script.

Each message type should have matching localization keys in every supported language:

```yaml
PERFORM_my_action_ACTION_SETUP: "When this action is performed."
PERFORM_my_action_ACTION_LOG: "The action was performed."
PERFORM_my_action_ACTION_MAP: ""
```

If the message type block is missing, the engine logs `Failed to find message type: PERFORM_<action_id>_ACTION`.

#### Generic Action Mouse Buttons

An `action_button` can bind independent generic actions for each mouse button:

```gui
left_action = { action_name = "my_left_action" }
right_action = { action_name = "my_right_action" }
```

Use `right_action` for a single right click. `right_click_and_hold_action` is a separate
hold-to-confirm interaction and should be used only when holding the button is intentional.
Each bound action remains a complete generic action: it needs its own `potential`, `allow`,
guarded `effect`, AI-list entry, message type, and localization. This is confirmed by
`reference_game_files/game/in_game/common/generic_actions/readme.txt:88-91`.

#### Cross-Mod Singleton Copies

`messagetypes.txt` and customizable-localization databases such as
`character_title.txt` are winner-takes-all full-file databases, not additive
registries. A later winning copy must contain every entry needed by the enabled
mods whose earlier copies it overrides. Dependency metadata alone is not enough:
in this project the Engineering Department copy loaded last despite the main
mod declaring it as a dependency, which hid 81 main-mod message types at
runtime. If the playset manually sorts the main TV mod after Engineering
Department, the standalone Engineering Department copy may contain only its own
entries, while the main TV copy must contain the TV + Engineering Department
union. Validate the vanilla prefix and each root's expected singleton coverage.

### 5.5. Variable Arithmetic (`change_variable`)

EU5 does **not** have `multiply_variable` or `divide_variable` commands. All in-place variable arithmetic uses `change_variable` with a named operator:

```pdx
change_variable = { name = my_var multiply = 100 }        # literal number
change_variable = { name = my_var divide = var:other_var } # variable reference
change_variable = { name = my_var multiply = var:factor }  # variable reference
change_variable = { name = my_var add = country_tax_base } # country scope property
```

Confirmed: `multiply = var:X` and `divide = var:X` are both valid (verified `cmm_core_slider_setting_effects.txt:223`).

`change_variable` does not accept `value =`. Use `set_variable = { name = my_var value = 1 }` for absolute assignment, and use `change_variable = { name = my_var add = 1 }` (or `subtract`, `multiply`, `divide`) for arithmetic. Using `value =` inside `change_variable` logs `Failed to read 'value' for 'change_variable'`.

#### Cross-Scope Numeric Variables

Do not use `prev.var:X` as the numeric right-hand side of comparisons or arithmetic after entering another scope. It can work as a scope reference, but in numeric contexts it may log errors such as `Invalid right side during comparison 'var'` and make the condition fail.

For trigger comparisons, use `root.var:X` only when `root` is verified to be the original numeric owner:

```pdx
var:stockpile ?= {
    this >= root.var:monthly_cost
}
```

The same rule applies in nested location/province effect blocks. Plain `var:X` always reads the
current scope's variable store, so after switching into `capital = {}`, `var:site ?= {}`, or
`every_location_in_province = {}`, use `root.var:X` for country-owned numeric inputs:

```pdx
var:tv_wonder_site ?= {
    add_location_modifier = { modifier = some_modifier years = root.var:country_years }
    change_prosperity = root.var:country_prosperity_gain
}
```

When country-scoped logic can run for broad country sets, `capital = { ... }` also needs a
nullable-link guard before the scope switch. In trigger or `limit` checks, use
`capital ?= { ... }`; do not put `exists = capital` beside a later direct `capital = { ... }`
and expect short-circuiting. Countries without a valid capital can otherwise log
`Event target link 'capital' returned an invalid object`.

For effect iterators, capture the number before switching scope and use the local variable inside the iterator:

```pdx
set_local_variable = { name = monthly_cost value = var:monthly_cost }
every_international_organizations_member_of = {
    change_variable = { name = stockpile subtract = local_var:monthly_cost }
}
remove_local_variable = monthly_cost
```

This also applies to variable-map key iterators and local-variable comparisons. Do not write
`local_var:current ?= var:outer_value` inside the iterator; EU5 can log `Invalid right side
during comparison 'var'`. Capture `var:outer_value` into another local before the iterator.
For dynamic numeric equality, compare locals with `NOT = { local_var:current < local_var:outer }`
and `NOT = { local_var:current > local_var:outer }`.

Treat `local_variable` values as explicit scratch state, not as automatically disappearing
temporaries. Clean every scratch value with `remove_local_variable = <name>` after its final use,
preferably at the direct top level of the effect so the cleanup is not skipped by a conditional
branch. For newly edited high-risk effects, add `# @validate_local_variable_cleanup` near the top
of the effect; `scripts/validate.py` then requires every `set_local_variable` in that marked
top-level block to have a later top-level cleanup line.

### 5.6. Ordered Global List Rebuilds

When using `ordered_in_global_list` to build rank 1..N outputs, treat the output variables as a fresh snapshot each time:

1. Clear all old rank variables before rebuilding.
2. Rebuild the pool and ensure every pool entry has the numeric variables used by `order_by`.
3. Guard rank N with `global_variable_list_size = { name = pool value > N-1 }` before running the ordered pass.

Do not rely only on `has_variable = previous_rank`. That may be a stale output from a previous rebuild. If the current pool has fewer candidates, a later ordered pass can execute with no selected item; `prev` becomes `none`, producing wrong-type errors when stored with `set_variable`, and adjacent `var:` reads may also log failed fetches.

### 5.7. Government Type Trigger

EU5 does **not** have the EU4 `government = monarchy` trigger. Use:

```pdx
government_type = government_type:monarchy       # in a trigger block
```

Valid government type IDs (source: `00_default.txt`):

| ID | Description |
|---|---|
| `monarchy` | All monarchy forms |
| `republic` | All republic forms |
| `theocracy` | All theocracy forms |
| `tribe` | Tribal nations |
| `steppe_horde` | Steppe horde nations |

Monthly government power variables (for use in `set_variable = { name = X value = legitimacy }` etc.):

| Government | Variable |
|---|---|
| monarchy | `legitimacy` |
| republic | `republican_tradition` |
| theocracy | `devotion` |
| tribe | `tribal_cohesion` |
| steppe_horde | `horde_unity` |

### 5.8. Location Prosperity Scale

Location `prosperity` reads are signed fractional values, not 0..100 percent points. Vanilla checks include `prosperity < 1`, `prosperity >= 0.75`, and `prosperity < -0.1`. When deriving a recovery priority from average prosperity, use the raw average directly; for example, `max(0, -average_prosperity)` makes negative prosperity compete on the same 0.x scale as other weights.

Do not divide an already-read `prosperity` value by 100 before comparing, storing, or using it as a weight. That extra scaling can make the resulting value too small to ever beat normal priority weights.

### 5.9. Optional Location Rank Checks In Selectors

Generic action selectors can repeatedly evaluate `visible` and called `effect` logic while the selection window is open. In that context, location iterators such as `any_neighbor_location` may visit objects that do not have a valid `location_rank`. A direct check such as:

```pdx
any_neighbor_location = {
    location_rank = location_rank:city
}
```

can log `Event target link 'location_rank' returned an invalid object`. Use optional rank comparisons instead:

```pdx
my_location_is_city_trigger = {
    location_rank ?= location_rank:city
}
```

Do not rely on `trigger_if = { limit = { is_land = yes } ... }` to protect a direct `location_rank = ...` read in selector/tooltip contexts; the evaluator may still prefetch the direct link.

### 5.10. Religion Conversion Targeting

Vanilla `promote_religion` treats a province as a valid conversion target when any contained location either has a dominant religion different from its owner or has incomplete local religious unity:

```pdx
OR = {
    NOT = { dominant_religion = owner.religion }
    local_religious_unity < 1.0
}
```

Source: `reference_game_files/game/in_game/common/cabinet_actions/promote_religion.txt:73-76`.

For direct cabinet-action/province eligibility, do not treat `dominant_religion != owner.religion` as the whole conversion-need check. A location can have the state religion as its dominant religion while still containing minority non-state-religion pops, and `local_pop_conversion_speed` can still be useful there.

For broader regional priority heuristics, follow the mechanic's design intent rather than blindly copying the vanilla OR. Governor's House autonomous religion conversion intentionally uses only the share of owned locations whose dominant religion is not the governing country's religion, ignoring minority cleanup once the state religion is dominant.

### 5.11. Subject Type Availability (`vassal` vs `samanta`)

Never hardcode `make_subject_of = { type = subject_type:vassal ... }` as the only outcome of a subjugation-style effect. `subject_type:vassal`'s `visible`/`creation_visible` blocks require `NOT = { has_advance = samanta_advance }` on the overlord (`reference_game_files/game/in_game/common/subject_types/vassal.txt:17,38`), so any country that has researched `samanta_advance` (the Indian-subcontinent feudalism advance) cannot create vassals at all — the action's `make_subject_of` call fails/no-ops for that overlord.

`subject_type:samanta` (`reference_game_files/game/in_game/common/subject_types/samanta.txt`) is the vanilla substitute: its `creation_visible` is simply `has_advance = samanta_advance`. The two are mutually exclusive by design (one requires the advance, the other forbids it), so a script that creates subjects on behalf of a player-chosen overlord must branch on the overlord's `has_advance = samanta_advance` and pick `subject_type:vassal` or `subject_type:samanta` accordingly, e.g.:

```pdx
if = {
    limit = { NOT = { scope:actor = { has_advance = samanta_advance } } }
    scope:target = { make_subject_of = { target = scope:actor type = subject_type:vassal } }
}
else = {
    scope:target = { make_subject_of = { target = scope:actor type = subject_type:samanta } }
}
```

Vanilla peace-treaty code exposes a native `can_make_subject_of = { target = <overlord> type = subject_type:<x> }` trigger (`reference_game_files/game/in_game/common/peace_treaties/subjugate_neighbor_native.txt:24`) that encapsulates a subject type's full `visible`/`creation_visible` eligibility; every confirmed vanilla usage is inside a peace-treaty `potential`/`create_enabled` block evaluated during an active war (`scope:war` in scope). Prefer the direct `has_advance = samanta_advance` branch above for subjugation logic that runs outside a war/peace-treaty context, since that condition is verified to work in any scope.

## 6. Game Content Modding

This section covers the modding of specific game content types.

### 6.1. Events

Events are pop-up messages that present the player with information and choices. They are defined in `.txt` files within the `in_game/events/` folder. Unlike EU4, EU5 does not use `mean_time_to_happen` for events; all events must be fired explicitly through on_actions, decisions, or other scripts. [7]

#### Event ID Range

Event IDs use `<namespace>.<integer>`, and the numeric part must be below 10000. Runtime logs from `jomini_eventmanager.cpp:141` reject IDs such as `tv_engineering_department.50011` with "not a valid event ID, has to be < 10000"; duplicate-ID errors may appear afterward as parser fallout.

For generated systems, do not encode high-cardinality dimensions directly into the event ID. Dispatch large dimensions before firing the event, and keep any event-local branch limited to a small dimension that is already scoped to that event, such as ceremony style inside a single wonder finalization event.

#### Event Option Tooltips

When hovering over an option button, the tooltip is rendered by `ContextualTooltipType` (defined in `eventwindow.gui`). It has two parts:

- **Title line**: `EventOption.GetText` — returns the option's `name` field as a plain string, **not** resolved through the localization system in this context. In debug mode this shows the raw key (e.g., `my_event.1.option_a`). This is expected behavior; vanilla options behave identically.
- **Content**: `EventOption.GetTooltip` — shows the output of any `custom_tooltip` entries inside the option block.

To add meaningful hover content, use `custom_tooltip = <key>` explicitly inside the option block and define the key in the localization file. The `.tt` suffix (e.g., `my_event.1.a.tt`) is a community convention — it must be referenced via `custom_tooltip`, it is **not** picked up automatically.

```
# event file
option = {
    name = my_event.1.a
    custom_tooltip = my_event.1.a.tt
    ...
}

# localization file
my_event.1.a: "Option button text"
my_event.1.a.tt: "Tooltip description shown on hover."
```

Event options may also pre-evaluate their `effect` stack while building tooltips. Do not assume a `set_variable` earlier in the option or in a called helper is committed before a later visible helper reads that variable. If an option sets `X` and then calls code that compares `var:X`, wrap the state-changing/application sequence in `hidden_effect = { ... }`, or guard the reusable helper with `has_variable = X` before direct `var:X` comparisons. For option triggers that read optional variables, prefer `var:X ?= N`.

Event options are already effect lists. Do not put `effect = { ... }` directly inside `option = { ... }`; the engine treats it as an effect command named `effect` and logs `Unknown effect effect`. Put visible effect calls directly in the option block, and use `hidden_effect = { ... }` only when the effect chain should be hidden from the option tooltip.

For event options, `hidden_effect` hides output but is still part of the option stack that hover rendering can evaluate. It is therefore not a performance boundary. Keep event-option hidden blocks to cheap guards or a scheduler such as a silent trigger, and move heavy hidden work into a `hidden = yes` event's `immediate` block or another path that is not rendered on every tooltip hover. The Engineering Department wonder finalization chain was refactored this way: inauguration options now call a light hidden scheduler, while `tv_engineering_department.6202` runs the expensive per-wonder/per-style construction, cleanup, broadcast, cache, and project-clear logic from its hidden event `immediate`.

For daily or other short-interval background work, a delayed silent hidden event can be used as a self-rescheduling loop. Seed it once from a lifecycle point with a persistent sentinel and `trigger_event_silently = { id = tv_feature.900 days = 1 }`. Define `tv_feature.900` as a `hidden = yes` country event; in `immediate`, first verify both the feature prerequisite and the loop sentinel, then do the daily work and schedule itself again with the same delayed silent trigger. On teardown, clear the active/sentinel variables so any already queued event arrives, fails the guard, and does not reschedule. Keep the numeric event ID below 10000, and never seed the loop repeatedly without a sentinel because each seed creates another independent chain.

```txt
tv_feature_start_daily_loop_effect = {
    if = {
        limit = {
            has_variable = tv_feature_active
            NOT = { has_variable = tv_feature_daily_loop_active }
        }
        set_variable = { name = tv_feature_daily_loop_active value = 1 }
        trigger_event_silently = {
            id = tv_feature.900
            days = 1
        }
    }
}

tv_feature.900 = {
    type = country_event
    hidden = yes

    immediate = {
        if = {
            limit = {
                has_variable = tv_feature_active
                has_variable = tv_feature_daily_loop_active
            }
            # daily work here
            trigger_event_silently = {
                id = tv_feature.900
                days = 1
            }
        }
    }
}
```

If a visible option helper needs a derived numeric value, prefer branching from persistent state and using literal effect values instead of writing a temporary variable and later passing `value = prev.var:X` or `value = scope.var:X`. In one Engineering Department finalization chain, the option computed extra building levels in `tv_wonder_final_building_extra_levels`, then a nested helper compared and reused that temporary variable; tooltip pre-evaluation logged invalid-left-side and unset-variable errors before the player clicked the option. The same trap reappeared when Prosperity M1 reinitialized partially built wonders and tried to collapse 1..6 module levels through temporary `*_combinable_levels` / `*_helper_extra_levels` scratch variables, and again when post-unit-completion hover rebuilt helper/module buildings through temporary `*_helper_current_level` / `*_target_module_level` variables. For bounded wonder-module merges or rebuilds, emit one literal branch per level and apply fixed building deltas directly from persistent state. For rounded division displays such as remaining-month counters, prefer verified script-value operators like `ceiling = yes` instead of scratch multiply/check variables. Also re-check persistent prerequisites at the event option boundary because confirmation events can stay open after state changes elsewhere.

If that visible helper also switches into a location/province block, do not keep using plain
`var:X` for country preview values. Inside the nested block, `var:X` reads the location/province
variable store; use `root.var:X` or a pre-captured `local_var:X` for country-owned numbers such
as `change_prosperity` or `add_location_modifier years = ...`.

Generic action widgets can hit the same problem while the action card or tooltip is merely visible. If an action effect initializes variables and then calls a visible helper that compares those same variables, action hover pre-evaluation may read them before the initialization is committed. Hide action widgets until their prerequisite state exists, repeat important prerequisites inside the action effect, and write reusable helpers with `var:X ?= ...` or threshold-style comparisons instead of direct reads of values that are only set earlier in the same chain. This also applies to display refresh helpers that set a scratch/display variable to 0 before comparing it later; if the helper is reachable from a visible generic action, the comparison should still be optional.

### 6.2 On Action Hook Extension

Vanilla hardcoded on_actions such as `on_annex`, `on_winning_war`, `on_join_war`, `on_ending_war`, `on_war_declared`, `on_ruler_death`, and `on_work_of_art_created` already define direct `effect = { ... }` bodies in `_hardcoded.txt`. A mod file that defines the same hook with another direct `effect` does not append to the vanilla body; Jomini logs "There is more than one 'effect' defined using most recent" and keeps only the latest effect block.

Extend those hooks with an `on_actions` delegate and keep the mod logic in a named callback:

```txt
on_war_declared = {
    on_actions = { tv_example_on_war_declared }
}

tv_example_on_war_declared = {
    effect = {
        # TV logic here, with the same scopes as the parent hook.
    }
}
```

For vanilla singleton pulses and shared hardcoded/general hook registrations, use the on_action bridge registry generator. It emits a TV-owned `tv_pulse_bridges.txt` bridge instead of vanilla filenames or feature-local parent hook blocks, and registers TV callbacks through `on_actions = { ... }` rather than copying vanilla pulse bodies.

#### Monthly Country Pulse Event Delay

When `country_monthly_pulse` checks the conditions for a player-facing event, fire that event one day later. The delay separates monthly condition scanning from event execution. Direct scripted-effect/on_action event fires use:

```txt
trigger_event_non_silently = { id = tv_example.1 days = 1 }
```

Native on_action `events` and `random_events` blocks use a delay entry before the event ids:

```txt
random_events = {
    chance_to_happen = 10
    delay = { days = 1 }
    1 = tv_example.1
}
```

`on_actions.info` documents `delay = { days = ... }` for event/on_action firing entries, and vanilla/reference scripted effects use `days = 1` inside `trigger_event_*` object forms. In Towards Victory, the configured value is `settings.monthly_country_pulse_event_delay_days` in `data/pulse_registry.yaml`, and `scripts/validate.py` walks registered monthly pulse callbacks plus TV helper calls to enforce the rule.

#### Tracking Completed Advances When the Engine Count Is Broken

The mirrored EU5 on_action definitions contain no callback for "an Advance finished research".
In the EU5 build tested by Towards Victory, the engine `num_advance_researched` interface
(exposed in script as `num_of_advances_researched`) also remained stuck after new research.
Therefore a reliable complete replacement must poll known Advance ids with `has_advance`.

Keep this scan off monthly country pulses. Towards Victory's dedicated
`gen_tv_science_score_effects.py` generator writes the scanner to its own
`tv_science_score_effects.txt` file from every top-level definition under
`reference_game_files/game/in_game/common/advances/`. The victory situation initializes only
player-controlled countries, and `yearly_country_pulse` rebuilds only countries passing
`is_ai = no`. The generated effect must carry an explicit temporary-workaround comment so the
file and callback can be removed once the upstream count works again.

#### Scripted Effect `custom_description` Localization

Any `custom_description = { text = KEY ... }` inside `common/scripted_effects` needs a matching `KEY = { ... }` entry under `in_game/common/effect_localization/`. A YAML localization entry by itself is only the player-facing string; it is not the effect-localization registry entry the engine validates at load. Missing entries produce `No effect loc KEY` and `PostValidate of effect 'custom_description' returned false`.

For simple static tooltip lines, positive perspectives can map back to the same YAML key, but negative perspectives still need distinct loc ids. Reusing the positive loc id for `global_neg`, `first_neg`, `third_neg`, `global_past_neg`, `first_past_neg`, or `third_past_neg` logs `Negative and positive version share loc for effect loc KEY` at startup. For generated static lines, emit paired `*_negative_text` YAML keys even when the text is only a short negated narration.

#### Scripted Effects That Change IO Variables

If a reusable `scripted_effect` changes an International Organization type variable and callers need to show the gain/loss in their option or action tooltip, do not leave the IO-scope `change_variable` bare inside the helper. Wrap the real effect in `custom_description` and register that `text` key under `in_game/common/effect_localization/`.

Vanilla uses this pattern for HRE, Middle Kingdom, and Catholic Church authority helpers:

```txt
custom_description = {
    text = change_imperial_authority_text
    value = $value$
    change_variable = {
        name = imperial_authority
        add = $value$
    }
}
```

The `effect_localization` entry maps the custom description to perspective-specific localization keys, including negative variants. The player-facing strings still live in `main_menu/localization`. This lets a scripted effect call display the signed IO variable change while executing the real `change_variable`.

For generic action or event hover contexts, keep the third-person effect localization strings self-contained. The GUI can pre-evaluate `custom_description` text before a `COUNTRY` promote target exists, so strings such as `[COUNTRY.GetName] gains ...` in `third` or `third_past` perspectives can spam `COUNTRY.GetName` data errors while the user hovers an action button. Prefer neutral strings such as `Gains $VALUE|+$ #Y $var$#!`.

#### Event-Created Artwork

For event-created named artworks, do not rely on `create_art` with only `artist` and `quality`. Vanilla named artworks specify both `type = work_of_art_type:<type>` and `key = <loc_key>` inside `create_art`, with the key localized in `main_menu/localization`. Without an explicit key, dynamically created works can end up unnamed; if the real `create_art` must branch by `artist_type`, use visible `if`/`else_if` branches so the actual creation effect appears in the option tooltip.

### 6.2. Countries

Countries are defined in two parts: a **country definition** file in `in_game/setup/countries/` that sets the tag, color, and culture, and a **country setup** file in `<top_folder>/setup/start/` that defines the starting situation, including owned provinces, capital, and ruler. [8]

### 6.3. Localization

All text displayed to the player is handled through the localization system. Localization files are in `.yml` format and must be encoded in **UTF-8-BOM**. Each language has its own subfolder and file naming convention (e.g., `_l_english.yml`). The system supports dynamic text, color formatting, and icons. [9]

Keep each localization key/value on one physical line. When a value needs an intentional line break, emit `\n` inside the quoted string; a real newline inside the value makes the next physical line parse as a new key and can produce `Invalid character` / `Missing colon` startup errors.

When using color formatting, put a separator after the color tag before player-facing text or generated placeholders. Use `#Y Text#!`, `#G {group}#!`, or `#R 30#!`, not `#YText#!`, `#G{group}#!`, or `#R30#!`. The localization formatter can otherwise read the adjacent content as part of the formatting tag and drop or mangle the highlighted span.

#### Text Format Tag Catalog

EU5 localization text formatting is `#tag content#!` — every tag must be closed with `#!`, and (per the rule above) needs a separating space before the content. This is not markdown; the available tags below were confirmed empirically by grepping `reference_game_files/game/main_menu/localization/english/*.yml` (2026-07-10), since there is no single reference file for the full tag list (`textformatting.gui` is a `gfx`-adjacent asset pruned from `reference_game_files/` by `sync_reference.py`).

Color tags (single letter):
- `#R` red (negative/warning, e.g. `#R lose#!`)
- `#G` green (positive, e.g. `#G 100#!`)
- `#Y` yellow (neutral highlighted value, most common)
- `#W` white/strong emphasis (e.g. difficulty labels)
- `#V` alternate highlight color
- `#L` light gray (secondary/de-emphasized value)
- `#P` / `#N` gray "enabled/positive" vs "disabled/negative" labels (e.g. `Enabled`/`Disabled`)
- `#X` bright red/danger (e.g. invalid-savegame warnings)
- `#D` debug-only gray (`_debug_l_english.yml`)
- `#F` flavor-text gray italic (explanatory asides)
- Lowercase variants `#r #g #y` exist for the same colors at a different inline weight/size

Style tags:
- `#bold` / `#italic` — matches its name
- `#weak` — grayed-out/de-emphasized text
- `#high` — highlighted/emphasized text
- `#T` — tooltip section header style (e.g. `#T Current Offer#!`)
- `#subtle_name` — low-emphasis style for proper-noun-style values (religion/climate names, etc.)

Tabular tooltip tags (used together to lay out tooltip columns, see `general_tooltips_l_english.yml`):
- `#col_t` — column header cell
- `#col_m` — column "middle"/secondary cell
- `#col` — regular column cell

Special-behavior tags:
- `#TOOLTIP:$BREAKDOWN_TAG$ content#!` — makes the wrapped value hoverable to show a scripted value breakdown (used for computed numeric values throughout tooltips)
- `#indent_newline:N content#!` — indents wrapped content by N levels after a line break
- `#trigger_pass` / `#trigger_fail` — colors/icons text to match a trigger's pass/fail state

Before inventing a bespoke solution for a localization display need (e.g. a custom color, a manual tooltip breakdown, hand-rolled tabular alignment), check this catalog first — it covers most needs already used throughout vanilla localization.

For TV's own six-way semantic mapping (positive/negative effect, neutral value, important emphasis,
beginner tip, flavor text) onto this tag catalog, see `CLAUDE.md` section "Localization Text
Formatting Convention" — that table is canonical; do not re-derive it ad hoc per file.

Event localization scope variables can be read directly from script scopes such as `ROOT` and `THIS`:

```yaml
my_event.1.desc: "Current value: [ROOT.GetVariable('my_var').GetValue|0]"
```

Do not insert `MakeScope` after `ROOT` or `THIS` in event localization. `ROOT.MakeScope.GetVariable(...)` treats an already script-scoped object like a GUI object and can log `Could not find promote for 'MakeScope'` / `Failed converting statement`. Use `Country.MakeScope.GetVariable(...)`, `Location.MakeScope.GetVariable(...)`, and similar chains only when the starting object is a GUI-layer binding such as `Country`, `Location`, `Player`, or a typed view object.

Generic action title/description localization can be fetched through a contextless prefetch path
before or alongside the real hover render. A scoped expression such as
`SCOPE.sCountry('actor')...` may display correctly in the real tooltip and still spam
`No context supplied ... wanted context of type 'Container'` from that prefetch. For action
description keys that must stay dynamic and read player-country state, prefer a
context-independent global binding such as `Player.MakeScope.GetVariable(...)`; use an explicitly
scoped GUI widget/tooltip only when the text needs non-player scopes. Do not replace requested
dynamic action text with static fallback merely to silence the log.

#### Customizable Localization Syntax and Usage

Unlike other Paradox games, EU5 custom localization is not called with a bare loc key — it is called with the data function `Custom('custom_localization_name')`, where the name refers to a scripted block defined in `in_game/common/customizable_localization/`. This is a conditional-text system: the engine picks one of several localization keys at read time based on triggers evaluated in a fixed scope, rather than the caller choosing a key directly.

Each customizable localization block has:
- a **top-level block name** — this is the database key passed to `Custom('...')`, and is itself a non-additive database entry (see below)
- `type` — the scope the block's triggers evaluate in (e.g. `country`, `character`, `building`)
- `random_valid` — optional, defaults to `no`. If `no`, the engine uses the *first* `text` entry whose trigger passes. If `yes`, the engine picks *randomly* among all `text` entries whose trigger passes.
- one or more `text = { trigger = { ... } localization_key = ... }` entries, evaluated top-to-bottom in the block's `type` scope
- an optional `fallback = yes` entry — its `trigger` is ignored, and it is used only when no other `text` entry validates. Do not rely on `always = no` inside a `fallback` entry to mean "never used"; `fallback = yes` is what makes it the catch-all.

Example block (`in_game/common/customizable_localization/`):

```
ruler_residence = {
    type = country
    random_valid = yes

    text = {
        trigger = {
            government_type = government_type:monarchy
        }
        localization_key = custom_royal_palace
    }

    text = {
        trigger = {
            government_type = government_type:republic
        }
        localization_key = custom_presidential_palace
    }

    text = {
        trigger = {
            any_owned_location = { is_coastal = yes }
        }
        localization_key = custom_seaside_palace
    }

    text = {
        trigger = { always = no }
        fallback = yes
        localization_key = custom_palace
    }
}
```

Every `localization_key` referenced above (`custom_royal_palace`, `custom_presidential_palace`, `custom_seaside_palace`, `custom_palace`) must still be defined as an ordinary key in a `.yml` localization file — the customizable localization block only selects *which* key resolves, it does not itself hold the display string.

**Calling it from localization text:** use `Custom('block_name')` chained off a scope promote, the same way any other data function is chained. For example, inside an event description:

```yaml
ruler_killed_event.1.d: "Our ruler was killed yesterday, while at the [ROOT.GetCountry.Custom('ruler_residence')]."
```

The engine evaluates `ruler_residence`'s triggers against `ROOT.GetCountry` (matching the block's `type = country`) and substitutes whichever key's text resolves for that scope — so the same loc line can render as "royal palace", "presidential palace", "seaside palace", or the "palace" fallback depending on live game state, without scripting a triggered_desc or separate loc keys per case in the calling text itself.

This is the mechanism to prefer over hand-rolled `triggered_desc`-in-loc chains when the *only* thing that varies per-scope is a noun/phrase substitution driven by simple triggers — it keeps the conditional logic in one script block instead of duplicating trigger conditions across every calling loc string.

#### Replacing Existing Non-Event Database Keys

Repeating an existing non-event top-level database key with its bare name does not imply an
override. EU5 rejects the later definition and logs `Duplicated key <key> will not be created`.
Use the `REPLACE:` prefix on the overriding definition:

```txt
REPLACE:university = {
    # Complete vanilla building block plus the mod's changes.
}

```

The same prefix applies to copied scripted effects and trigger-localization database entries.
Keep the complete source block unless that database type explicitly supports partial merging; the
prefix changes which definition wins, but does not reconstruct omitted properties. Generated
non-event overrides must add `REPLACE:` in the generator so regeneration cannot restore the
duplicate-key bug.

#### Modifying Base-Game Events

`REPLACE:` and `INJECT:` do not modify individual base-game events. Create a new file in the
mod's `in_game/events/` folder whose filename sorts before the relevant base-game event file,
such as `0000_modded_events.txt`. At its top, repeat the event's vanilla namespace and copy only
the complete event blocks being changed with their bare IDs:

```txt
namespace = prices

prices.1 = {
    # Complete vanilla event block plus the mod's changes.
}
```

One file may patch multiple namespaces, provided each group of events immediately follows its
respective namespace declaration.

The duplicate event-ID error in `error.log` is expected and harmless: the early-loaded event is
the active definition. If the copied event invokes a scripted effect or trigger defined inside
the original event file, either inline that helper's contents into the event or copy the helper
under a distinct mod-specific name. Redefining the original helper name breaks later base-game
events; omitting it leaves the early event unable to resolve the helper.

#### Customizable Localization Database Keys

Customizable localization files under `in_game/common/customizable_localization/` are parsed as database entries keyed by the top-level block name. These keys are not additive merge blocks. For example, adding a second file with `character_title_prefix = { ... }` causes the engine to ignore the duplicate and log `Duplicated key character_title_prefix will not be created`.

To extend character title prefixes, generate or copy the full vanilla `character_title.txt` and insert custom `text = { ... }` entries into the existing `character_title_prefix` block instead of creating a separate same-key file.

## 7. Advanced Modding Topics

### 7.1. Interface (GUI) Modding

The user interface is highly moddable through `.gui` files. The system is modular, using templates and types to create reusable UI components. Creating new windows and widgets allows for the development of complex new game features. [10]

GUI `text = "KEY"` properties are localization lookups. If the key is missing from `main_menu/localization`, the engine logs `Unlocalized text 'KEY'` from `pdx_gui_localize.cpp`. Correct the key to one defined by the current data/localization set, add the key for all supported languages, or use `raw_text` only when the intended display is a literal string.

For non-clickable dynamic text, GUI can resolve a generated key directly with
`text = "[Localize(Concatenate('PREFIX_', ToString_int32(FixedPointToInt(value))))]"`.
The Engineering Department proposal text at
`src/in_game/gui/panels/organization/tv_engineering_department.gui:556` is the
working local precedent. This is appropriate for ordinary localized prose such
as a ceremony stage's active/completed flavor sentence; it does not create or
link a game concept. Continue to use a registered raw concept id with
`SelectGameConcept` only when a clickable concept link is required.

The same `text = "[Localize(Concatenate(...))]"` route can render a dynamically
chosen inline font icon: make each generated localization value exactly
`@icon_name!`, where `icon_name` is validated against
`main_menu/gui/shared/font_icons.gui`. This is the right pattern for compact,
data-owned state badges such as unique-wonder ceremony steps. Keep the icon
selection with the per-entity/per-step data and emit a key containing both
identifiers; do not replace it with a global position-to-icon map, a
`GetConceptTexture` illustration, or an unbounded set of static GUI branches.

Community Mod Menu registration ids are also a namespace, not just a label.
The `mod_id` passed to `cmm_register_*` becomes part of the generated setting
ids, callback flags, and cached metadata names that the menu uses to populate
the mod list. Keep that namespace short and distinct from gameplay ids. A very
long CMM id can make the project disappear from the in-game menu even when the
registration blocks are otherwise correct. In Engineering Department, `tv_ed`
is the CMM namespace, while gameplay-facing aliases stay under
`tv_engineering_department_*`.

CMF's Mod Action Log is the shared in-game audit trail for mod actions, especially
host/global tools in multiplayer. Do not build a TV-owned parallel log. Call
CMF's helper effects from country scope, because the current country is recorded
as the actor. Use `cmf_log = { action = tv_key }` for action-only text, and
`cmf_log_with_args = { action = tv_key arg1 = tv_arg1 arg2 = tv_arg2 }` when
both arguments are localization keys. The rendered text is `[arg1] [action]
[arg2]`. For country arguments, save scopes as `cmf_log_arg1` and
`cmf_log_arg2`, then call `cmf_log_with_scope_args = { action = tv_key }`; for
a single country argument, save only `cmf_log_arg2` and call
`cmf_log_with_scope_arg = { action = tv_key }`. Define every TV action key and
custom flag argument in both supported localization languages. `cmf_clear_log =
yes` exists, but CMF's own clear button is hidden in multiplayer, so TV code
must not expose a separate multiplayer clear route. Reference implementation:
`reference_mods/3692202776/in_game/common/scripted_effects/cmf_log_effects.txt`
and `reference_mods/3692202776/in_game/gui/cmm/panes/cmm_log_pane.gui`.

GUI `raw_text` does not expand `$LOCALIZATION_KEY$` substitutions. A value such as `raw_text = "@trade! $TV_TRADE_LEAGUE_IO_COLUMN$"` renders the `$TV_TRADE_LEAGUE_IO_COLUMN$` text literally. For static localized labels with icons, use `text = "TV_TRADE_LEAGUE_IO_COLUMN"` and put `@trade! ...` inside the localization value. For dynamic values that must use `raw_text`, split the localized label into a separate `text` widget if needed.

GUI image `fittype` values are EU5-specific, not CSS object-fit names. Vanilla examples use values such as `centercrop`, `fill`, `start`, and `end`; `fittype = contain` logs `Unknown fit type 'contain'` during GUI loading.

`modify_texture` belongs to a rendered image layer such as `background` or `icon`, not to a layout container. A named block can hide this boundary: if a reusable card type defines `block "card_bg"` at its `vbox` level, a `blockoverride "card_bg"` also writes into that `vbox`; placing `modify_texture` beside `using = bg_paper_card_situations` therefore logs `Property 'modify_texture' not handled` and can fail the widget's property setup. Put conditional texture modifiers inside a real background layer instead, as vanilla does in `attribute_columns/cabinet_action.gui`:

```gui
blockoverride "card_bg" {
    background = {
        using = paper_card_texture
        modify_texture = {
            visible = "[MyCondition]"
            using = color_light_green_texture
            blend_mode = overlay
        }
    }
}
```

When replacing a template-backed card background, retain its original background layers, texture density, frame/stretch settings, and base overlays before appending the conditional modifier. Do not remove a dynamic state color merely to avoid the property error.

Custom game concepts require both localization and a definition in `main_menu/common/game_concepts/`. A localization pair such as `game_concept_tv_foo` / `game_concept_tv_foo_desc` does not create the concept by itself. If `[tv_foo|e]` is used before `tv_foo = { texture = "..." }` is registered, the localization parser treats `tv_foo` as a data-system function and logs `Could not find data system function 'tv_foo'`.

The in-game Europedia (Encyclopedia) has no native, data-driven way to register a new sidebar page/category — the `Encyclopedia.AccessPages`/`EncyclopediaPage` collection is engine-populated and read-only (getters only: `GetTitle`, `Self`, `AccessSelf`), and a `game_concept`'s `family` field is a thematic tag with no page/category effect in vanilla's own `encyclopedia_lateralview.gui`. A dedicated browsable tab requires fully overriding `in_game/gui/encyclopedia_lateralview.gui` and toggling two mutually-exclusive content trees with a `GetVariableSystem` variable (one button sets it, every vanilla page button clears it, both sides gate their `visible=` on `HasValue`/`Not(HasValue)`) — the only working precedent found, confirmed against released community mod `3613232232`. See `docs/knowledge/risk_cards/europedia.md` and `src/in_game/gui/encyclopedia_lateralview.gui` (the `tv_encyclopedia_active` tab toggle + `tv_encyclopedia_filter` category filter, with a generated card list reusing existing `game_concept_<id>`/`_desc` pairs rather than authoring new prose).

Dynamic game-concept links are safe only when the dynamic value is a registered raw concept id. In a location-window test, a flag-derived value localized before link parsing, so `SelectGameConcept(dynamic_key, ...)` effectively tried to resolve a localized display name as a concept id and logged `Could not find data system function`. Do not feed concept-link helpers `GetFlagName` or other localization-prone values. For generated dynamic routes, store a numeric id and build registered ids such as `tv_wonder_display_<id>` for `SelectGameConcept(...)` / `[...|E]`; use `Localize(Concatenate('game_concept_', key))` only for intentionally plain, non-clickable text.

`GetFlagName` is not a safe raw-key accessor for script variables or variable-map values. In a location-window dynamic display test, a value written as `flag:tv_wonder_unique_pharos_lighthouse` rendered through GUI as `法罗斯灯塔`, so string concatenation produced invalid keys such as `game_concept_法罗斯灯塔` and `法罗斯灯塔_level_3`. For display projections that must recover script keys, store a numeric id and generate static id branches, or use a typed datamodel object with a verified `GetKey` accessor.

GUI `texture = "[...]"` expressions need a function/object that returns a texture-like value, not an arbitrary CString path. In the location-window dynamic display test, `GetConceptTexture(Concatenate(...))` rendered, but all raw DDS path forms built with `Concatenate` stayed blank: nested path+filename, suffix-only `.dds`, and even `Concatenate('gfx/.../file.dds', '')`. Use `GetConceptTexture` as a dynamic routing bridge when no typed datamodel object is available. For arbitrary mod DDS files, register image-only game concepts such as `tv_wonder_display_image_<id>` whose `texture` points at the DDS, add matching `game_concept_*` and `game_concept_*_desc` localization, then build that concept id from a numeric slot id in GUI.

`ShowModifierEffect(Concatenate(...))` can build the correct modifier id at runtime, but the GUI expression alone may not make the engine/static lookup path recognize every generated modifier. For generated display modifier routes such as `tv_wonder_display_<id>_level_<level>` or `tv_wonder_display_<id>_local_level_<level>`, keep the dynamic GUI route and add generated unreachable script references:

```txt
tv_reference_display_modifiers_effect = {
    if = {
        limit = { always = no }
        add_country_modifier = { modifier = my_display_country_modifier years = -1 mode = add_and_extend }
        capital = {
            add_location_modifier = { modifier = my_display_location_modifier years = -1 mode = add_and_extend }
        }
    }
}
```

The `always = no` guard prevents runtime state changes while leaving static modifier references in a loaded script file.

Every generated static display modifier also needs matching `STATIC_MODIFIER_NAME_<id>`
localization in each supported `main_menu/localization` language. The modifier database
requests the name key even when the modifier is display-only; missing keys can fall back to
generated text such as `STATIC MODIFIER NAME tv trade chain strength display 18980`.

`add_country_modifier` validates against static country modifiers, not `common/auto_modifiers`.
Country Auto modifiers can drive real automatic country effects through their own
`potential_trigger`, but their ids are invalid database objects for
`add_country_modifier`, including in scripted-effect tooltip previews. For Engineering
Department wonders, auto-driven country effects are applied by Country Auto modifiers,
while generated static mirrors are kept for GUI `ShowModifierEffect` display and
unreachable database references only. Do not restore old finalization-time static
grants/removals or route scripted-effect tooltip previews through those old static ids for
effects whose real lifecycle is building-gated Country Auto modifiers.

For ordinary localization keys such as building names, use `$key$` substitution instead of square-bracket game concept syntax. GUI-bound localized text can parse `[building_key|E]` as a data-system function when `building_key` is not registered as a game concept, producing `Could not find data system function '<key>'`.

For building type display names in localization text, use the engine helper `[ShowBuildingTypeName('building_key')]` or `[ShowBuildingTypeNameWithNoTooltip('building_key')]`. Do not use `[GetBuilding('building_key').GetName]`; `GetBuilding` is not a valid localization data function and GUI-bound localized text can fail parsing with `Failed to find type 'GetBuilding'`.

`MakeScope.GetVariable('x')` returns a GUI variable wrapper, not an arbitrary typed object constructor. Do not chain `.GetGoods` or `.GetInternationalOrganization` from it. Goods icons/names must come from a real typed goods datacontext such as `Trade.GetGoods` or `GoodsMarketEntry.GetGoods`, or from static generated branches keyed by a saved numeric goods id. `OpenInternationalOrganizationView(...)` likewise needs a typed `InternationalOrganization` object from a verified GUI chain such as `InternationalOrganization.Self`, `OrgItem.GetOrg.Self`, or `GetUniqueInternationalOrganization('hre').Self`; a saved script variable cannot be promoted with `.GetInternationalOrganization`.

GUI boolean helpers are arity-specific. `And()` and `Or()` take exactly two operands; for three operands use `And3()` / `Or3()` as vanilla GUI files do, and for larger expressions nest binary helpers. A three-argument `And(a, b, c)` logs `Function 'And' expected 2 arguments, got 3` and the widget statement fails conversion.

In IO member lists from `InternationalOrganizationsView.GetMemberItems`, keep the outer group filter on real `MemberTypeItem` predicates such as `MemberTypeItem.IsAllMembers`. A display-name comparison like `EqualTo_string(MemberTypeItem.GetName, ShowSpecialStatusName('tv_alliance_member_status'))` can hide every row. For leader filtering inside `MemberTypeItem.GetCountries`, compare matching country objects, e.g. `Not(ObjectsEqual(Country.Self, InternationalOrganizationsView.GetInternationalOrganization.GetLeaderCountry.Self))`; `IsIOLeaderCountry(Country.Self)` has produced `FetchData failed` in that row context. Row-level custom-panel buttons likewise should not write direct `enabled = "[UIAction.IsEnabled]"` unless the context is verified to expose `UIAction`. Conventional `action_button` / `action_button_diamond` templates remain valid when the widget defines a real `left_action`; if errors persist after changing action widgets, restart or fully reload the panel before assuming the current source is still failing. When a row button passes a country into a generic action that reads `scope:target`, pass a script scope with a button-level `parameter_value = "[Country.MakeScope]"`. `Country.Self` is appropriate for GUI object comparisons, but it can leave `scope:target` unset for guarded action effects, producing a silent no-op.

Build-location selector helpers require typed GUI objects. Vanilla calls `SelectLocationToBuildDefault(BuildingItem.GetBuildingType)` or `SelectLocationToBuildDefault(LocationBuildingItem.GetBuilding.GetType)`. Do not pass a literal building key string such as `SelectLocationToBuildDefault('my_building')`: the click can still play a following audio effect, but the build-location interface will not open. If a custom panel has no `BuildingType` data context, route the button through a `generic_action` with `looking_for_a = location` and perform `construct_building` in a guarded effect.

For fixed-position icon overlays, avoid percentage `position` values directly on `icon` widgets. In the Governor's House power-balance bar, `position = { 50% 0 }` on an `icon` rendered at the left edge instead of the midpoint. Use pixel positions when the parent has a fixed size, or position a `widget` wrapper with percentages and place the icon inside that wrapper. Vanilla percentage-position examples such as `progressbars.gui` use positioned `widget` wrappers.

The shared `situation_panel` template includes a default `situation_subheader_content` block with a 45px row. Custom situation panels that do not use a subheader should explicitly add `blockoverride "situation_subheader_content" {}` near the top of the panel. Vanilla situation panels such as `colonial_revolution.gui` and `council_of_trent.gui` use this empty override to avoid an unwanted blank band above the main content.

When a widget is a direct child of `hbox` or `vbox`, the box layout owns placement and sizing. Do not set `parentanchor` on those children, and do not use percentage components in their `size` values such as `size = { 97% 72 }`. Use `layoutpolicy_horizontal`, `layoutpolicy_vertical`, stretch factors, or non-percent fixed/min/max sizing instead. For `io_character_card` in an `organization_custom_content` block, vanilla panels rely on the type's built-in `layoutpolicy_expanding` rather than adding a percentage `size` or `parentanchor`.

`progressbar` does not handle `margin_top`. If a progressbar needs vertical offset or centering inside an `hbox`/`vbox`, put a fixed-size wrapper `widget` in the layout and anchor the progressbar inside the wrapper with `parentanchor` / `widgetanchor`, leaving the progressbar itself free of `margin_top`.

Keep `ignoreinvisible` on layout containers, not on plain `widget` wrappers. A generic image wrapper `widget` with `ignoreinvisible = yes` logs `Property 'ignoreinvisible' not handled` and fails property setup for the `uberwidget`. For conditional illustration areas, set `visible = ...` on the wrapper and put the actual images in child widgets with their own `visible` expressions.

Zeroing a reusable card type's header height does not hide its header content, and stacked cards need an explicit height. A card template built like this project's `tv_engineering_department_card_common` (`type ... = hbox { widget = { block "header_size" {...} ... block "common_header" { block "common_header_icon" {...} block "common_header_text_full" {...} } } ... }`) still creates and renders the default `common_header` icon+text even when the caller does `blockoverride "header_size" { size = { -1 0 } }` — that size override only constrains the header widget's own declared bounds, not its child content, so the default placeholder icon+title overflows the collapsed parent and appears as a leaked duplicate above the card. To make a card genuinely untitled, also `blockoverride "common_header" {}` (empties the icon+text block itself). Separately, a plain `widget` wrapper in this codebase's GUI convention does not auto-size vertically from its child content the way `hbox`/`vbox` do — every working stacked-card usage sets `layoutpolicy_vertical = fixed` plus an explicit numeric `minimumsize`/`maximumsize` height directly on the card instantiation. Omitting it collapses every card to zero height, so a `vbox` of such cards renders them all piled on the same position instead of listed in sequence. See `docs/knowledge/risk_cards/wonders.md` rule 22.

The "expanding child blows out a bounded parent" failure above recurs even when the numbers look safe on paper. The ceremony cards' text column sat in an extra `widget = { layoutpolicy_horizontal = expanding text_multi = { max_width = 380 ... } } }`, and even though 380 fit the arithmetic budget (card width minus margin minus icon column minus spacing), the rendered text column still measured ~375px and pulled the fixed-500-wide card wider than its declared bound — because the expanding wrapper widget doesn't respect an ancestor's size clamp at all, regardless of whether the inner content numerically fits. Do not wrap `text_multi` in an extra expanding `widget`; place it directly as the `hbox` child with `layoutpolicy_horizontal = expanding`, `max_width`, and `autoresize = yes` set on the `text_multi` itself (verified precedent: `tv_engineering_department.gui:8422-8428`), and keep `max_width` with a comfortable safety margin below the arithmetic budget rather than flush against it.

An auto-height ("shrinking") chain must be unbroken from the outermost flexible card down to the actual variable-height content — one hardcoded-height wrapper anywhere in the middle caps the whole chain. The pattern is: `layoutpolicy_vertical = shrinking` + `size = { W -1 }` on each nested wrapper `widget`, and `set_parent_size_to_minimum = yes` + `layoutpolicy_vertical = shrinking` on each nested `vbox`, repeated at every level between the card and its content — not just the first level. A card whose outer instantiation and first-level wrapper both correctly use this pattern can still fail to grow if a second- or third-level wrapper further in reverts to an old fixed `size = { W N }` with no shrinking policy (e.g. a leftover from when that area only ever held much shorter content); that single link caps the measured content at its hardcoded number regardless of how much actually renders inside it, so new variable-count content silently overflows past the card instead of stretching it taller.

When a conditional illustration is a fixed preview column with mutually exclusive background images, give the wrapper explicit bounds and size the visible preview child to fill them. `layoutpolicy_expanding` alone does not guarantee a button or background texture will paint at the intended size; if the preview sits inside a plain `widget`, the child `button` can shrink to the natural width of its content unless it also fills the card. In wonder-location panels, keep the existing card/hbox/vbox structure, make the clickable wrapper fill the card, give the image column its own fixed width, and size the preview widget with fixed pixels that match the content area.

Do not put paragraph-style localized text in an unconstrained `hbox` elastic column. A pattern like `hbox = { ... widget = { layoutpolicy_horizontal = expanding size = { -1 92 } text_single = { multiline = yes ... } } }` can let the text's natural width flow back into the row. In the Engineering Department IO, this made a child `vbox` expand to 548.3px while its parent card content was correctly bounded at 470px. Use a fixed-width text area, preferably a small card/container with `text_multi`, `max_width`, and `autoresize`:

```gui
widget = {
    size = { 368 92 }
    using = bg_text_mask_container_dark_blue
    vbox = {
        margin = { 8 8 }
        text_multi = {
            max_width = 352
            autoresize = yes
            text = "MY_PARAGRAPH_LOC_KEY"
            align = nobaseline|left
        }
    }
}
```

Vanilla IO header help text uses the same bounded `text_multi` pattern with `max_width` and `autoresize`.

The above guards against a row growing too wide; the opposite failure — a row collapsing too narrow — has a different, easy-to-miss cause. An `hbox`/`vbox` that declares an explicit `size = { W H }` alongside a mix of fixed and expanding children (e.g. a fixed-width icon column plus an expanding `text_multi`) must also set `layoutpolicy_horizontal = expanding` on the container itself. Without it, the container does not honor its own declared `size` at all: it falls back to sizing off the sum of its children's intrinsic minimums, and a `text_multi` with no `minimumsize` has an intrinsic width of ~0 until layout stretch is applied. The net effect is the whole row silently collapsing to roughly the fixed column's width, with the expanding text column rendering at effectively 0 width (and consequently unselectable/unhoverable). `max_width`/`autoresize` on the `text_multi` itself does not substitute for this container-level property — both are required together. See `docs/knowledge/risk_cards/wonders.md` rule 11 and `docs/knowledge/anti_patterns.yaml` rule `hbox_explicit_size_without_layoutpolicy_horizontal_collapses_to_content_width` for the verified instance (`tv_engineering_department.gui`'s ceremony stage cards) and working precedent citations.

Standalone `io_character_card` widgets inherit `character_entry` name sort highlights. Those highlights call `FilteredSortedList.IsKeyHoveredByWidgetName`, which only works when a `FilteredSortedList` datacontext exists. For cards shown in custom IO panels, situation panels, or other non-sortable contexts, override both inherited highlight blocks:

```gui
blockoverride "name_highlight" {}
blockoverride "character_entry_name_sort_by_highlight" {}
```

Vanilla `middle_kingdom.gui` applies these exact overrides with a comment that they block error log spam.

For GUI lists backed by a `datamodel`, each `item = { ... }` block is an item description, not a general layout container. It must contain exactly one top-level child widget and no direct properties. If a row needs both content and a divider, wrap both inside a single parent `vbox` or `widget`:

```gui
item = {
    vbox = {
        hbox = { }
        widget = { using = bg_divider_flavor_01 }
    }
}
```

Putting sibling widgets directly under `item` logs `Malformed item desc`, and can produce nearby text formatter noise while the list is rendered.

When embedding `RequirementsList` directly in a panel to show `ShowTriggerConditions(...)`, do not hide its title with an empty `blockoverride "block_title" {}`. The underlying list/header stack uses tooltip header text styling that reads `ExtraTooltipInfo.GetTintColor`; outside a real tooltip context, exposing that header can spam `No context supplied ... ExtraTooltipInfo.GetTintColor` while the panel is hovered. If the list should be titleless, preserve the nested title block and hide it explicitly:

```gui
blockoverride "block_title" {
    block "block_title" {
        visible = no
    }
}
```

Likewise, do not use `TooltipTextBlock` as a normal always-visible panel widget. `TooltipTextBlock` inherits `tooltip_text_block_template`, and that template's text color block reads `ExtraTooltipInfo.GetTintColor`. In a real tooltip (`ContextualTooltipType`, `AlertTooltipType`, etc.) that context exists; in a normal panel it does not. For ordinary UI text, use `text_single` or `text_multi` instead.

When a tooltip row combines `TooltipStringPairList` / `TooltipTextBlock` with a preview image, avoid hard-coding the row to `size = { W H }` or wrapping the modifier block in an `expanding` child. That can keep the frame visually short while the visible text spills below the border. Prefer width-fixed, height-auto rows instead: constrain the row with `size = { W -1 }` or `minimumsize`, let the visible content contribute its own height through `set_parent_size_to_minimum`, and keep the parent container `ignoreinvisible = yes` so hidden rows do not reserve space.

That last point undersells a sharp edge: `set_parent_size_to_minimum = yes` computes the vbox's own size from the MINIMUM size each child reports — not from any `layoutpolicy_horizontal`/`size` set on the vbox itself or on its parent `widget`. Giving the *row/container* a `minimumsize` is not enough if the actual visible leaf inside it is a bare `text_multi` with only `max_width`/`autoresize`/`layoutpolicy_horizontal = expanding` and no `minimumsize` of its own — that leaf reports 0 intrinsic width, which zeroes out the whole chain: the vbox (and any ancestor `widget` that in turn auto-fits to it) collapses to margin-only width, and the text renders unselectable at effectively 0 width, with no error in the log. Two plausible-looking fixes do NOT work here and were confirmed not to by live measurement: adding `ignoreinvisible = yes` to an unrelated sibling container, and adding/removing `layoutpolicy_horizontal`/`layoutpolicy_vertical`/explicit `size` on the ancestor `widget`/`vbox` — the vbox stayed stuck at exactly its own doubled horizontal margin regardless. The actual fix is to give the LEAF `text_multi` its own `minimumsize = { W -1 }` matching its `max_width`, matching the vanilla `minimumsize = { W -1 }` + `autoresize` idiom (e.g. `reference_game_files/game/in_game/gui/advances_lateralview.gui:331-332`). See `docs/knowledge/risk_cards/wonders.md` rule 22's sixth follow-up and `docs/knowledge/anti_patterns.yaml` rule `set_parent_size_to_minimum_vbox_needs_leaf_minimumsize_for_width` for the verified instance.

For GUI scripted-effect tooltips, match the effect's scope links to the object passed by the GUI. `ShowScriptedEffectForScope('my_effect', LocationView.GetLocation.MakeScope.Self)` makes the current effect root the location itself. From that effect, country-owned reward lines should use:

```txt
owner ?= {
    add_country_modifier = { modifier = my_country_modifier years = -1 mode = add_and_extend }
}
```

Do not write `location.owner = { ... }` in this specific location-root tooltip context. The `location` prefix is parsed as an event-target link named `location`; when no separate `location` event target exists, hover evaluation logs a scope mismatch and may also leave `COUNTRY.GetName` unavailable for the generated modifier tooltip. `location.owner` remains valid only in contexts that expose a separate `location` event target, such as building `on_built`.

#### Engine-generated effect previews and GUI consumers

The engine generates descriptions for real scripted effects, including add_stability,
granting a randomly selected estate privilege, and dismissing a character. Nested calls,
conditional branches, and random selection do not inherently require manual descriptions
or a separate tooltip-only effect. The project owner confirmed that these rendered
automatically in the Engineering Department debate panel in 1.3 (2026-10-14).

Keep the real effect as the preview source of truth. A blank preview does not justify
substituting TV_ENGINEERING_SOLUTION_* strings, injecting those strings via custom_tooltip,
registering redundant trigger-localization entries, or duplicating execution branches in
new *_tooltip_effect wrappers. Genuine custom mechanics may still need their established
custom localization; this rule concerns replacing descriptions the engine already provides.

Trace the producer and its GUI consumer against these vanilla references, relative to
reference_game_files/game/:

| Output | Vanilla rendering example |
| --- | --- |
| ShowModifierEffect(...) | TooltipStringPairList in in_game/gui/economy_lateralview.gui |
| UIAction.GetEffects | TooltipStringPairList in in_game/gui/panels/organization/union.gui |
| UIAction.GetEffects | TooltipBlockList in in_game/gui/shared/government_tooltips.gui |
| EventOption.GetTooltip | TooltipTextBlock in in_game/gui/eventwindow.gui |
| UIAction.GetConditions | TooltipRequirementsList in in_game/gui/panels/organization/union.gui |

TooltipRequirementsList uses SetRequirementsListFromTextContextWithTitle and
RequirementsList.GetLines in main_menu/gui/shared/main_menu_cooltip_types.gui. It is a
requirements parser, not a universal effect renderer. ShowScriptedEffectForScope returns
CString in the official data-type reference; that type alone does not establish which
structured-list parser accepts its contents. Verify scope, output structure, receiver,
visibility, and width/height before changing the effect. Respect the separate rule against
using tooltip-only TooltipTextBlock in an ordinary panel without its required context.

Vanilla also embeds ShowScriptedEffectForScope directly in localization: see
main_menu/localization/english/events/expeditions/treasure_fleet_events_l_english.yml,
chinese_expedition_resolution_tt, and chi_expedition_resolution_very_positive in
in_game/common/scripted_effects/country_effects.txt. This previews conditional effects
without a dedicated tooltip wrapper.

Investigation status (2026-10-14): the claims that 1.4 cannot expand nested/random effects
or requires a tooltip wrapper were withdrawn. Experimental manual descriptions,
registrations, and duplicate wrappers were removed. The debate panel currently passes
the original effect to ShowScriptedEffectForScope and displays its result through
text_multi.raw_text. This implementation still awaits in-game verification; the final
renderer choice and exact cause of the original blank area are not yet established.

### 7.2. Map Modding

EU5 includes a powerful map editor for modifying the game world. This tool allows for editing the heightmap, terrain textures, and location setup. However, it has high system requirements, recommending at least 32GB of RAM. [11]

### 7.3. Graphics Modding

Flags in EU5 are generated dynamically through a scripted coat of arms system, a significant change from the static `.tga` files of EU4. This allows for flags to change based on triggers and game conditions. [12]

## 8. Best Practices and Resources

*   **Float precision limit**: The EU5 engine reads float literals to a maximum of **5 decimal places**. Any digits beyond the 5th are silently truncated. Always round generated or hand-written values to ≤5 dp (e.g. `0.08477` not `0.084771`). This is particularly relevant for generated script_values such as budget shares and demand scales.
*   **Wonder fixed modifier scale**: For wonder design data and generated wonder files, keep fixed-value `global_pop_assimilation_speed`, `global_pop_conversion_speed`, `local_pop_assimilation_speed`, `local_pop_conversion_speed`, `local_manpower`, and `local_sailors` values at or below `0.5`. EU5 multiplies these fixed values by 1000 in game, so `1` means roughly `1000`, not a 1% bonus. Use the matching `*_modifier` percent modifier when a percentage bonus is intended. `scripts/validate.py` enforces this on wonder paths.
*   **Subject loyalty modifier scale**: `subject_loyalty` is a country modifier measured in loyalty points, not a percent-style fraction. Vanilla advances use whole values such as `subject_loyalty = 5`; write `10` for a +10 subject-loyalty bonus, not `0.10`.
*   **Use a proper IDE**: Tools like VS Code with the CwTools extension can catch errors and improve readability.
*   **Avoid Overwriting Vanilla Files**: Create your own files and use the `replace_paths` feature or specific load orders to override game content. This improves mod compatibility.
*   **Use Version Control**: Git is an invaluable tool for tracking changes and collaborating with others.
*   **Consult Community Resources**: The official EU5 Wiki, the Paradox Forums, and community Discord servers are essential resources for any modder.

## 9. Conclusion

The modding architecture of European Universalis 5 represents a significant evolution from previous Paradox titles. With the power of the updated Clausewitz Engine and the flexible Jomini scripting layer, modders have an unprecedented ability to create new content and transform the game. While the learning curve can be steep, the extensive documentation and active community provide a strong foundation for success.

## 10. Building Types

### 10.1 Definition Structure

Buildings live in `in_game/common/building_types/`. Key fields verified against vanilla files (2026-05):

```
building_id = {
    is_foreign = no               # prevent foreign construction
    pop_type = clergy             # employment pop type
    max_levels = 1                # integer or scripted_int
    category = cultural_category  # see §10.2 for valid values
    expensive = yes               # UI flag only
    town = yes                    # location rank eligibility
    city = yes
    megalopolis = yes
    rural_settlement = no
    location_potential = { is_capital = yes }   # visibility filter; root = location
    country_potential = { ... }                 # country-level visibility; root = country
    allow = { ... }                             # construction conditions; root = location, scope:actor = building country
    build_time = large_capital_build_time       # time reference (NOT price = X)
    construction_demand = university_construction  # cost reference (NOT price = X)
    on_built = { ... }            # fires when construction completes; root = location
    on_construction_started = { ... }  # vanilla trade company construction-task hook
    on_construction_ended = { ... }    # vanilla trade company construction-task hook
    on_destroyed = { ... }        # fires when building is removed
    remove_if = { ... }           # auto-destroy trigger; root = building
}
```

**Critical: EU5 uses `construction_demand = X`, NOT `price = X` (EU4 style).** Using `price =` is silently ignored.

`on_construction_started` / `on_construction_ended` are used by vanilla `trade_company_headquarters` even though the official `types/building_types.txt` summary only lists `on_built`. Use `on_construction_ended` when a mechanic must react to building-level upgrades as well as first construction. If the completion is tied to the construction task itself, complete directly from this hook rather than requiring `location_building_level` to update inside the same callback.

**Modifier scope note:** `modifier` and `raw_modifier` are location effects. `capital_country_modifier` is a country modifier only when the building is built in the capital (verified in `reference_official_defines/types/building_types.txt`). For event-created buildings that may appear outside the capital, apply national effects separately with `add_country_modifier` and keep the building's own modifier local.

Boolean modifier types must use `yes` or `no`, not Python/YAML spillover values like `True`/`False` or numeric `1`/`0`. For example, `can_recruit_regiment_in_this_location`, `global_peasants_migration_allowed`, and `global_laborers_migration_allowed` are declared with `boolean=yes`, and vanilla scripts write these values as `yes` or `no`. In Python generators, handle `bool` before numeric branches because `bool` is an `int` subclass; otherwise `true` YAML values can become malformed `True` tokens or numeric burden values.

### 10.2 Valid Category Values

Confirmed from vanilla building definitions: `basic_industry_category`, `colonial_category`, `consumer_goods_category`, `cultural_category`, `defense_category`, `estate_category`, `government_category`, `infrastructure_category`, `military_category`, `naval_category`, `religious_category`, `rgo_building_category`, `trade_category`, `village_category`, `weapons_industry_category`.

For educational / scientific buildings: `cultural_category` (used by `university`, `library`, `art_school`).

### 10.3 Allow Block with custom_tooltip

The `allow` block uses `root = location`, `scope:actor = building country`. Custom tooltips wrap real triggers and display localized text when conditions pass (green) or fail (red):

```
allow = {
    custom_tooltip = {
        text = MY_TOOLTIP_KEY     # localization key
        scope:actor = { var:my_score_var ?= { this >= 100 } }
    }
    custom_tooltip = {
        text = MY_SECOND_TOOLTIP_KEY
        scope:actor = { var:my_prereq ?= { this >= 1 } }
    }
}
```

Multiple `custom_tooltip` blocks in `allow` are AND-combined. Each evaluates independently and shows its own green/red state. Source: `estate_buildings.txt`, `capital_buildings.txt`.

Do not use `has_variable = X` as a guard for `var:X = ...` or `var:X < N` inside generic action `allow`, `potential`, selector, or tooltip logic. The UI evaluator may still fetch direct `var:` links from sibling trigger blocks while building tooltips or rendering the action card. For nullable variables, use optional variable links (`var:X ?= ...`) so an absent variable returns false without logging an unset-scope error. For bounded less-than checks where no optional threshold syntax is verified, generate literal optional branches (`var:X ?= 0`, `var:X ?= 1`, etc.) plus an explicit unset branch if missing state should pass.

For custom generic-action buttons that call `construct_building`, do not rely on the building type's `max_levels` or a lone `can_build_building` check. Repeat the cap logic in a reusable trigger and call it from the action `allow`, any target picker `visible`/`enabled`, and the final effect guard. Country-wide caps should count queued construction with:

```
scope:actor = {
    total_building_levels_including_construction:my_building < 5
}
```

For one-per-location target pickers, also filter both existing and queued copies:

```
NOT = { has_building = building_type:my_building }
NOT = {
    any_buildings_in_location = {
        building_type = building_type:my_building
        building_levels_under_construction >= 1
    }
}
```

Otherwise the custom action can spend its scripted price while the final construction does nothing, especially from stale target lists or after the cap was reached by an in-progress level.

### 10.4 Actual Building Employment

`location_building_level(building_type:X)` reports completed levels, not current staffing. For mechanics that depend on actual workers, enter the building object from the location and read `building_employed_amount`:

```
scope:target_location = {
    ordered_buildings_in_location = {
        limit = { building_type = building_type:my_building }
        order_by = building_level
        max = 1
        scope:target_country = {
            set_variable = {
                name = my_actual_workers
                value = {
                    value = prev.building_employed_amount
                    multiply = 1000
                    floor = yes
                }
            }
        }
    }
}
```

`prev.building_employed_amount` is read from the building scope. Multiply by 1000 when the consuming mechanic stores people counts rather than pop-size units, as building `employment_size = 1` represents 1,000 workers in UI terms.

### 10.5 on_built Scope

`on_built` fires with root = location. Access the owning country via `location.owner = { ... }`. Source confirmed at `unique_buildings.txt:516-524` and `religion_buildings.txt:32-51`:

```
on_built = {
    hidden_effect = {
        location.owner = {
            set_variable = { name = my_var value = 1 }
            my_scripted_effect = yes
        }
    }
}
```

### 10.6 build_time References (verified)

| Reference | Context | Source |
|---|---|---|
| `large_capital_build_time` | Large government/capital buildings (royal court) | `capital_buildings.txt:15` |
| `guild_build_time` | Craft guilds | `common_buildings.txt:126` |
| `infrastructure_build_time` | Roads, irrigation | `common_buildings.txt:23` |
| `rural_build_time` | Rural production | `common_buildings.txt:218` |

### 10.7 construction_demand References (verified)

| Reference | Context | Source |
|---|---|---|
| `university_construction` | Universities, academies | `culture_buildings.txt:48` |
| `early_capital_building_construction` | Royal court, capital buildings | `capital_buildings.txt:56` |
| `village_construction` | Irrigation systems | `common_buildings.txt:32` |

## 11. Music

### 11.1 Music Player Tracks

EU5's exposed text-side music track database lives in `in_game/common/music_player_tracks/`.
The official type note and vanilla file both say new songs are first added in Wwise, then
registered by their Wwise event key. The text entry supports metadata only:

```
MusicPlayer_my_event_key = {
    composer = My_Composer_Key
    performer = My_Performer_Key
    soloist = My_Soloist_Key
}
```

Add matching `music_player_l_*.yml` localization for the track key, `<track>_flavour`,
and any composer/performer/soloist keys. The in-game music player GUI lists registered
track objects and plays them through `MusicPlayerTrack.Play`; current references do not
show EU4-style `songs.txt` trigger/chance rules for country, war, date, variable, or event
conditions.

Do not infer from this file that EU5 cannot trigger music. It can: vanilla GUI calls
`Audio_PlayEvent('mus_culture_track_start', 'music_manager')` when entering the game.
That is a Wwise/audio-manager event, not a `music_player_tracks` trigger rule. The
declare-war panel's visible button is a hardcoded `DeclareWarLateralView.GetDeclareWarAction`,
and `on_war_declared` is a hardcoded script hook with scopes for actor, recipient, and war.
If a mod needs conditional music, the verified routes are therefore:

- register the Wwise event key in `music_player_tracks` for player-visible metadata;
- trigger a Wwise music event from GUI with `Audio_PlayEvent(<event>, 'music_manager')`;
- use script hooks such as `on_war_declared` to set state or fire UI/events, then verify
  whether the desired audio event can be called from that context.

Current references still do not show a normal country/event effect that directly plays a
named music-player track by track key. The safe distinction is: `music_player_tracks`
registers tracks; Wwise/audio-manager events and hardcoded action hooks drive playback.

### 11.2 Audio Culture and Environment Tags

`main_menu/music/audio_culture_types/` defines audio culture archetypes such as
`european_sfx`, each with `priority` and `culture_tag`. Topography, vegetation, and some
climate definitions can provide `audio_tags`, which appear to feed ambient/environmental
audio selection rather than music-player song conditions.

## 12. References

[1] [Europa Universalis V - PC performance graphics benchmarks](https://en.gamegpu.com/test-gpu/rts-strategii/europa-universalis-v-test-gpu-cpu)
[2] [Grand Jomini Modding Information Manuscript](https://forum.paradoxplaza.com/forum/threads/grand-jomini-modding-information-manuscript.1170261/)
[3] Manus AI internal analysis of 16 EU5 mods from Steam Workshop, January 2026.
[4] [Mod structure - Europa Universalis 5 Wiki](https://eu5.paradoxwikis.com/Mod_structure)
[5] [Trigger - Europa Universalis 5 Wiki](https://eu5.paradoxwikis.com/Trigger)
[6] [Effect - Europa Universalis 5 Wiki](https://eu5.paradoxwikis.com/Effect)
[7] [Script value - Europa Universalis 5 Wiki](https://eu5.paradoxwikis.com/Script_value)
[8] [Event modding - Europa Universalis 5 Wiki](https://eu5.paradoxwikis.com/Event_modding)
[9] [Country modding - Europa Universalis 5 Wiki](https://eu5.paradoxwikis.com/Country_modding)
[10] [Localization - Europa Universalis 5 Wiki](https://eu5.paradoxwikis.com/Localization)
[11] [Interface modding guide - Europa Universalis 5 Wiki](https://eu5.paradoxwikis.com/Interface_modding_guide)
[12] [Map modding - Europa Universalis 5 Wiki](https://eu5.paradoxwikis.com/Map_modding)
[13] [Flag modding - Europa Universalis 5 Wiki](https://eu5.paradoxwikis.com/Flag_modding)
[14] User-provided Variable maps reference excerpt, pasted into the 2026-06-04 TV knowledge-capture task; source article noted some sections were last verified for EU5 1.1. Summarized in section 5.2 as a local authoritative source for `variable_map`.
