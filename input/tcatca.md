---
title: The Case Against TCA
date: 2024-11-27
tags: code,swift
slug: tcatca
---

The Composable Architecture ([TCA](https://github.com/pointfreeco/swift-composable-architecture)) is an iOS app development framework that promises "better state management", "modular design", and "testable side effects". After doing some consulting with a startup looking to adopt the framework, I can confidently say: TCA creates more problems than it solves.

#### Pain.

TCA is packed with unnecessary complexity, redundant abstractions, and frustrating quirks. The startup I worked with ultimately abandoned the framework for the following reasons:

- **Steep Learning Curve**: Requires mastering "reducers" and "stores" making onboarding difficult.
- **Excessive Boilerplate**: Even simple features require excessive code, slowing development.
- **Performance Problems**: Slow builds, indexing, and crashing Xcode previews waste time.
- **Compiler Issues**: Reducers often break the compiler with hard-to-diagnose errors.
- **Maintenance Burden**: Frequent updates break code and demand costly refactoring.
- **Hard to Remove**: Hard to rip out once adopted.
- **Third-Party Risk**: Maintained by essentially two people with no long-term guarantee.
- **Outpaced by SwiftUI**: SwiftUI now handles most problems TCA was built to solve.

I contend that the only good idea in TCA is the `DependencyClient` pattern. But you don't actually need TCA to implement the pattern, you can do it with just a few lines of swift (see my post on [the Client Pattern](/clientpattern)).

#### Obnoxious Dependencies

Importing TCA brings in 16 additional dependencies, most of which are other Point-Free libraries. While these libraries might have the `swift-` prefix, only `swift-collections` and `swift-syntax` are actually from Apple:

```
swift-composable-architecture 1.16.1
  ├── combine-schedulers 1.0.2
  ├── swift-case-paths 1.5.5
  ├── swift-clocks 1.0.5
  ├── swift-collections 1.1.3
  ├── swift-concurrency-extras 1.2.0
  ├── swift-custom-dump 1.3.3
  ├── swift-dependencies 1.4.0
  ├── swift-identified-collections 1.1.0
  ├── swift-macro-testing 0.5.2
  ├── swift-navigation 2.2.2
  ├── swift-perception 1.3.5
  ├── swift-snapshot-testing 1.17.5
  ├── swift-syntax 600.0.0-prerelease-2024-09-04
  ├── SwiftDocCPlugin 1.4.3
  ├── SymbolKit 1.0.0
  └── xctest-dynamic-overlay 1.4.0
```

This level of bloat is overkill for what TCA claims to solve, and the naming convention (`swift-navigation` instead of `point-free-navigation`) feels super obnoxious and deliberately disingenuous.

#### Online Sentiment

Looking through reddit (and elsewhere online) it seems that my frustrations are widely shared:

**[Reddit: Have you used TCA in production?](https://www.reddit.com/r/SwiftUI/comments/16pab2x/have_you_used_tca_in_production_whats_your/)**

- "TCA is basically an **extra layer of complexity** in order to do what SwiftUI already does under the hood."
- "Watch the first three [TCA] videos on how to make a checklist… The solution is **sooooo complicated.**"
- "[TCA] seems **needlessly complex** to jump through 5+ files just to figure out what’s happening on one simple screen."

**[Reddit: I hate the Composable Architecture](https://www.reddit.com/r/iOSProgramming/comments/1c1o5jx/i_hate_the_composable_architecture/)**

- "[TCA] adds **unnecessary complexity** and a central dependency."
- "Everything [in TCA] is so tightly connected, **any change leads to changes everywhere else.**"
- "Working two years with that [TCA] shit was **one of the reasons I quit the project.**"

**[Rod Schmidt: Composable Architecture Experience](https://rodschmidt.com/posts/composable-architecture-experience/)**

- "TCA is a 3rd party framework. This means **Apple doesn’t support it or care about it.**"
- "You have to **constantly re-learn things** as the [TCA] framework gets updated."
- "You can be **much more productive with MVVM** and get the same benefits [as TCA]."

#### Survey Results

Despite the criticism TCA is pretty popular. So who actually uses the framework? And why do they like it? To find out, I put up a [survey](https://docs.google.com/forms/d/e/1FAIpQLSdvFSCfHlHi3zjX643ZVv8Q0mBiqwBcf9FgBc4PJ-EOeZCvkw/viewanalytics) in a few iOS/Swift subreddits and got 100 responses:

```markdown
| TCA Opinion                                        | SwiftUI-first | UIKit-first |
| -------------------------------------------------- | ------------- | ----------- |
| I dont like it and avoid using it                  | 8             | 18          |
| I like it a lot and prefer it for app architecture | 5             | 19          |
| Its acceptable but not my preferred choice         | 1             | 19          |
| Not applicable (I havent used TCA)                 | 3             | 27          |
```

Key insights:

- **83%** of survey respondents started with UIKit, while only **17%** started with SwiftUI.
- **47%** of SwiftUI-first developers avoid TCA, compared to only **22%** of UIKit-first developers.

TCA's appeal seems rooted in its familiarity to UIKit-first developers, offering a structured, UIKit-like experience. For SwiftUI-first developers, TCA likely feels unnecessary and redundant, solving problems that SwiftUI already natively solves. 

#### Vanilla

So what's the alternative? Honestly, just vanilla SwiftUI! Frustrated with TCA, I decided to recreate the [SpeechRecognition](https://github.com/pointfreeco/swift-composable-architecture/tree/1.16.1/Examples/SpeechRecognition) example to prove that the framework is unnecessary.

Check out [my vanilla implementation](https://github.com/maxhumber/VanillaSpeechRecognition/blob/master/VanillaSpeechRecognition/SpeechRecognitionView.swift). Most of the code is in a single file (just for ease of comparison) and works seamlessly with **Xcode 16**, **Swift 6**, and **iOS 18**. Here are the important benchmarks:

```markdown
| Metric                      | Vanilla    | TCA             |
| --------------------------- | ---------- | --------------- |
| Dependencies                | 0          | 16              |
| "Cold" Build Time (seconds) | 1.1        | 32.4            |
| "Warm" Build Time (seconds) | 0.1        | 0.4             |
| Indexing Time               | Negligible | Several minutes |
| Lines of Code               | 319        | 579             |
```

Given that the vanilla version delivers the same functionality and testing capabilities without the complexity, boilerplate, or quirks, I just don't see the advantage of using TCA.

#### TL;DR:

The Composable Architecture might have been useful in 2019 when SwiftUI was still immature, but Apple's yearly updates have rendered it obsolete for most apps. TCA is a perfect example of over-engineering that actively makes code worse while claiming to make it better. If you're transitioning to SwiftUI, focus on mastering its native tools in lieu of adopting TCA just because it feels familiar.
