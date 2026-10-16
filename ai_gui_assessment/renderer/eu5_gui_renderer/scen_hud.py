"""Invented 1337 Hungary HUD data; this is not a save-game reconstruction.

Bindings follow the vanilla ingame_topbar, hud_topbar, hud_bot, and side bars.
Dynamic flags, character portraits, and the 3D map remain unsupported.  Keep
those limitations visible in the runner/report instead of substituting icons.
"""


UNSUPPORTED = (
    "3D world map and live save-game data",
    "Procedural country flag and animated flag scene",
    "Animated ruler/regent portrait",
)

GC = "gfx/interface/graphical_cultures/european_gfx/{}.dds"


def _estate(key, name, power, satisfaction, change, color):
    """Expose both EstatesItem and Estate aliases used by the vanilla bar."""
    icon = f"gfx/interface/icons/estates/{key}.dds"
    values = {
        "__type__": "Estate",
        "GetType": key,
        "GetType.GetMapColor": color,
        "GetRelativePower": power,
        "GetSatisfaction": satisfaction,
        "GetMonthlySatisfactionChange": change,
        "GetNameWithNoTooltip": name,
    }
    item = {"__type__": "EstatesItem", "GetEstate": values}
    for field, value in values.items():
        if field != "__type__":
            item[f"GetEstate.{field}"] = value
            item[f"Estate.{field}"] = value
    item[f"GetEstateIcon('{key}')"] = icon
    return item


def hud():
    """Return explicit expression regex/value pairs for the closed-panel HUD."""
    estates = [
        _estate("crown_estate", "王室", .18, .70, .001, (.69, .56, .20, 1)),
        _estate("nobles_estate", "贵族", .29, .64, .002, (.56, .30, .55, 1)),
        _estate("clergy_estate", "教士", .19, .72, .001, (.80, .70, .43, 1)),
        _estate("burghers_estate", "市民", .16, .58, -.001, (.72, .36, .24, 1)),
        _estate("peasants_estate", "农民", .18, .53, .0005, (.30, .51, .35, 1)),
    ]
    currency = {
        "gold": 1250, "stability": 35, "legitimacy": 82, "prestige": 46,
        "political_influence": 30, "diplomats": 3, "war_exhaustion": 0,
        "manpower": 24000, "sailors": 8000,
    }
    changes = {
        "gold": 12.4, "stability": .5, "legitimacy": .1, "prestige": .2,
        "political_influence": .3, "diplomats": .1, "war_exhaustion": 0,
        "manpower": 180, "sailors": 70,
    }
    maxima = {key: 100 for key in currency}
    maxima.update(manpower=40000, sailors=12000, diplomats=5)
    keys = "|".join(currency)
    country = {"__type__": "Country", "Exists": True,
               "GetName": "匈牙利", "GetNameWithNoTooltip": "匈牙利"}
    ruler = {"__type__": "Character", "GetName": "查理一世",
             "GetNameWithNoTooltip": "查理一世", "GetAge": 49,
             "IsRuler": True, "HasRebel": False, "IsCivilWarRuler": False}
    age = {"__type__": "Age", "GetNameWithNoTooltip": "传统时代",
           "Self": "age_1_traditions"}

    mocks = [
        (r"Character\.IsAlive|UIActionProvider\.IsVisible", True),
        (r"Character\.(HasArmy|HasNavy|HoldsCabinetPosition|IsHeadOfCabinet|IsRegent|IsReligiousOrderMember)", False),
        (r"Country\.IsGreatPower", True),
        (r"Country\.IsRegionalPower", False),
        (r"Country\.GetGreatPowerRank", 8),
        (r"GetLegitimacyIcon\(Country.GetGovernment.GetGovernmentType\)", 'gfx/interface/icons/resources/legitimacy.dds'),
        (r"CanUnpause|IsInmersionModeDisabled", True),
        (r"GetPauseBannerLabel", '已暂停'),
        (r"IsGameViewOpen\('agenda'\)", False),
        (r"InGameTopbar\.GetPlayer\.GetLongNameWithNoTooltip", '匈牙利王国'),
        (r"GetGraphicalCultureTexture\('(\w+)'\)", lambda m: GC.format(m[1])),
        (r"GetGraphicalCultureTextureForCountry\('(\w+)',[^)]*\)",
         lambda m: GC.format(m[1])),
        (r"InGameTopbar\.GetPlayer|GetPlayer|Player|Country", country),
        (r"InGameTopbar\.GetPlayer\.GetGovernment\.GetRulerOrRegent", ruler),
        (r"Country\.Exists|IsPlayerValid|Player\.IsValid|Country\.IsValid", True),
        (r"(?:Country|Player|GetPlayer)\.GetName(?:WithNoTooltip)?", "匈牙利"),
        (r"GetDateString", "1337年4月1日"),
        (r"TutorialHasVar\('[^']+'\)|TutorialIsRunning", False),
        (r"IsLobbyOpen|IsPauseMenuShown|IsTimeLineMode|HasErrors|GameIsMultiplayer", False),
        (r"IsLateralViewFullScreen|IsLateralViewMenuFullScreen|IsLateralViewBlockingMapRendering", False),
        (r"(?:LeftView|RightView)\.(?:IsShown|IsSideAttached)", False),
        (r"IsLateralGroup(?:Opened|Highlighted)\('[^']+'\)", False),
        (r"IsLateralViewOpened\('[^']+'\)|IsLateralViewOpenedWithParams\('[^']+','[^']+'\)", False),
        (r"IsObserving|IsObservingWithoutSelectedCountry|IsPlayerSubject", False),
        (r"IsGamePaused|IsGameUserPaused", True),
        (r"IsGameSystemPaused|ShouldPauseVignetteBeVisible", False),
        (r"IsSaving|IsWritingDumps|IsRecalculatingCacheData|IsPlayerHotjoining|IsDisconnecting", False),
        (r"IsGameSpeedEqualOrGreaterThan\('\(int32\)([1-5])'\)", lambda m: int(m[1]) <= 3),
        (r"CanChangeGameSpeed", True),
        (r"MPChatNewMessage|MPChatNewWhisper|IsMultiplayerChatShown|IsAnyPlayerLaggingBehind", False),
        (r"GroupItem\.IsCountry|GroupItem\.IsLocation", False),
        (r"MapModeSelectorVars\.(?:Exists\('[^']+'\)|HasValue\('[^']+','[^']+'\))", False),
        (r"IsMapModeMenuPinned|HasMapColorLedger|IsBuildDebug", False),
        (r"IsDefaultMapModeSet|CanChangeMapMode", True),
        (r"InGameTopbar\.GetEstates", estates),
        (r"Country\.GetGovernment\.GetEstateFromKey\('crown_estate'\)\.GetType", "crown_estate"),
        (r"GetEstateIcon\('(crown_estate|nobles_estate|clergy_estate|burghers_estate|peasants_estate)'\)",
         lambda m: f"gfx/interface/icons/estates/{m[1]}.dds"),
        (rf"Country\.Get(?:FixedPoint)?CurrencyValue\('({keys})'\)", lambda m: currency[m[1]]),
        (rf"Country\.IsCurrencyValueEqualOrLessThanZero\('({keys})'\)", lambda m: currency[m[1]] <= 0),
        (rf"Country\.GetCurrencyMaxValue\('({keys})'\)", lambda m: maxima[m[1]]),
        (rf"InGameTopbar\.GetPlayerCurrencyChange\('({keys})'\)", lambda m: changes[m[1]]),
        (rf"InGameTopbar\.GetPlayerCurrencyChangeFormatted\('({keys})'\)",
         lambda m: f"+{changes[m[1]]:g}" if changes[m[1]] > 0 else f"{changes[m[1]]:g}"),
        (r"Country\.GetTotalPopulationNoLink", "8.42M"),
        (r"Country\.GetLastMonthsPopulationText", "+12.4K"),
        (r"Country\.GetLastMonthsPopulationChange", 12400),
        (r"Player\.GetTotalCoastalPopulation", 1800000),
        (r"Player\.GetDiplomacy\.GetNumOfDiplomats", 3),
        (r"Player\.GetDiplomacy\.GetMaxNumOfDiplomats", 5),
        (r"Country\.GetModifierValueNoFormat\('monthly_diplomats'\)", .1),
        (r"Player\.GetCurrentResearch\.IsActive", False),
        (r"Player\.GetCurrentResearch\.GetProgress", 0),
        (r"GetHighlightAnim\('5\.0, 0\.0, 0\.2'\)", 0),
        (r"GetCurrentAge", age),
        (r"Age\.GetNameWithNoTooltip", "传统时代"),
        (r"GetCurrentAgePercentage", 0),
        (r"GetAgeIcon\((?:Age\.Self|'age_1_traditions')\)", "gfx/interface/icons/age/age_1_traditions.dds"),
        (r"GetPlayer\.GetDiplomacy\.GetInternationalOrganizations", []),
        (r"GetRelationsUILimit", 4),
        (r"GetPlayer\.GetGovernment\.HasActiveRegent", False),
        (r"Character\.IsRuler", True),
        (r"Character\.HasRebel|Character\.IsCivilWarRuler", False),
        (r"IsMusicPlayerPaused", True),
        (r"LateralView\.IsRightPanel", False),
        (r"LateralView\.IsLeftPanel", True),
        (r"PdxGuiWidget\.(?:HasTooltipMetaTitle|HasTooltipMetaGameConcept|IsTooltipLocked)", False),
        (r"PdxGuiWidget\.(?:IsUberButtonVisible|IsUberButtonEnabled)", True),
        (r"ExtraTooltipInfo\.HasUIAction|ExtraTooltipInfo\.TooltipIsReady|UsesTimerLocking", False),
        (r"ExtraTooltipInfo\.GetTintColor|GetDebugFontColor", None),
    ]
    return mocks
