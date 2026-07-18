---
title: SwiftUI Data Flow
date: 2024-11-26
tags: code,swift
slug: swiftuiflow
---

SwiftUI is over 5 years old. While a lot has changed since its introduction at WWDC19, the fundamentals— especially with respect to data flow—remain pretty much the same. Sure, there's some new [Observation](https://developer.apple.com/documentation/Observation) framework syntax to learn, but Apple has done a great job at "simplifying" and "unifying" APIs while maintaining backwards compatibility.

This post is meant to serve as a reference guide for modern (iOS 17/18+) SwiftUI data flow. It ought to be particularly useful for working with LLMs that might crank out outdated code.

## Data Flow

By "data flow" I mean: how data moves through an app and updates the UI. Data flow in SwiftUI is actually quite simple... as long as you keep two principles in mind: views automatically update when their data changes, and every piece of data needs a single source of truth. 

Since its release Apple has produced hundreds of hours of WWDC videos on SwiftUI. If you just watch these three videos you'll be like 90% up to speed:

- [Data Flow Through SwiftUI (WWDC19)](https://developer.apple.com/videos/play/wwdc2019/226/)
- [Data Essentials in SwiftUI (WWDC20)](https://developer.apple.com/videos/play/wwdc2020/10040/)
- [Discover Observation in SwiftUI (WWDC23)](https://developer.apple.com/videos/play/wwdc2023/10115/)


## Value vs Reference

I don't want to get too in the weeds, but in order to see and understand how data flow has changed we have to differentiate between value types (📦) and reference types (🔗). 

Value types like Strings and Ints and Doubles and Bools and structs and enums, create independent copies when assigned. In contrast, reference types, like classes, share the same instance. 

Apple [strongly recommends](https://www.swift.org/documentation/articles/value-and-reference-types.html) using value types for most cases. If we followed this advice more often I wouldn't have even need to write this post as most of the data flow changes in SwiftUI (from iOS 13/14 to iOS 17/18+) are related to reference types!

## Timeline

Legend: `✅` = current, `⛔` = avoid, `📦` = value, ` 🔗` = reference

**iOS 13 / WWDC19**

- `✅` `📦` **`@State`**
- `✅` `📦` **`@Binding`** 
- `⛔` `🔗` `ObservableObject` *replaced with **`@Observable`** in iOS 17+*
- `⛔` `🔗` **`@Published`** *redundant when using **`@Observable`** in iOS 17+*
- `⛔` `🔗` **`@ObservedObject`** *replaced with **`@Bindable`** in iOS 17+*
- `⛔` `🔗` **`@EnvironmentObject`** *replaced with **`@Environment`** in iOS 17+*
- `✅` `📦` **`@Environment`**
- `⛔` `📦` `EnvironmentKey` *replaced with `@Entry` in iOS 18+*
- `⛔` `PreviewProvider` *replaced with `#Preview` in iOS 17+*

**iOS 14 / WWDC20**

- `⛔` `🔗` **`@StateObject`** *replaced with `@State` in iOS 17+*

**iOS 15 / WWDC21**

- No significant data flow changes

**iOS 16 / WWDC22**

- No significant data flow changes

**iOS 17 / WWDC23**

- `✅` `🔗` **`@Observable`** *replaces `ObservableObject`*
- `✅` `🔗` **`@State`** *replaces `@StateObject`*
- `✅` `🔗` **`@Bindable`**† *replaces `@ObservedObject`*
- `✅` `🔗` **`@Environment`** *replaces `@EnvironmentObject`*
- `✅` `#Preview` *replaces `PreviewProvider`*

**iOS 18 / WWDC24**

- `✅` `📦` `@Entry` *replaces `EnvironmentKey`*


## Rosetta Code

Here's a simple, but practical, example of modern data flow in SwiftUI (I'd encourage you to copy-and-paste this block of code into Xcode to experiment with the syntax for yourself):

```swift
// iOS 17/18+
import SwiftUI

extension EnvironmentValues {
    // ✅ 📦 replaces `EnvironmentKey`
    @Entry var lastRefresh: Date = .now
}

// ✅ 🔗 replaces `ObservableObject`
@Observable
class UserStore {
    var username = "max" // ✅ 🔗 replaces @Published
    var hasPremium = false // ✅ 🔗 replaces @Published
    
    func randomize() {
        username = String((0..<3).map { _ in "abcdefghijklmnopqrstuvwxyz".randomElement()! })
    }
}

// ✅ 🔗 replaces `ObservableObject`
@Observable
class EmojiStore {
    var emoji = "😀" // ✅ 🔗 replaces @Published
    
    func update() {
        emoji = String(UnicodeScalar(Int.random(in: 0x1F600...0x1F64F))!)
    }
}

struct ParentView: View {
    @State var lastRefresh: Date = .now // ✅ 📦 unchanged
    @State var userStore = UserStore() // ✅ 🔗 replaces `StateObject`
    @State var emojiStore = EmojiStore() // ✅ 🔗 replaces `StateObject`
    @State var count: Int = 0 // ✅ 📦 unchanged
    
    var body: some View {
        VStack(spacing: 15) {
            HStack {
                Text("Last Refresh: \(lastRefresh.formatted(date: .omitted, time: .complete))")
                Button("Refresh") { lastRefresh = .now }
            }
            HStack {
                Text("Username: \(userStore.username)")
                Button("Randomize") { userStore.randomize() }
            }
            HStack {
                Text("Has premium: \(userStore.hasPremium ? "Yes" : "No!")")
                Button("Toggle") { userStore.hasPremium.toggle() }
            }
            HStack {
                Text("Emoji: \(emojiStore.emoji)")
                Button("Update") { emojiStore.update() }
            }
            HStack {
                Text("Count: \(count)")
                Button("+1") { count += 1 }
                Button("-1") { count -= 1 }
            }
            ChildView(
                emojiStore: emojiStore, // ✅ 🔗 unchanged
                count: $count // ✅ 📦 unchanged
            )
        }
        .padding()
        .background(Rectangle().stroke(.purple, lineWidth: 1))
        .environment(\.lastRefresh, lastRefresh) // ✅ 📦 unchanged
        .environment(userStore) // ✅ 🔗 replaces `.environmentObject`
    }
}

struct ChildView: View {
    @Environment(\.lastRefresh) private var lastRefresh: Date // ✅ 📦 unchanged
    @Environment(UserStore.self) private var userStore: UserStore // ✅ 🔗 replaces `@EnvironmentObject`
    @Bindable var emojiStore: EmojiStore // ✅ 🔗 replaces `@ObservedObject`
    @Binding var count: Int // ✅ 📦 unchanged
    
    var body: some View {
        VStack(spacing: 15) {
            HStack {
                Text("Last Refresh: \(lastRefresh.formatted(date: .omitted, time: .complete))")
            }
            HStack {
                Text("Edit username:")
                @Bindable var userStore = userStore // ⚠️ 🔗 FRUSTRATING!
                TextField("", text: $userStore.username)
                    .textInputAutocapitalization(.never)
                    .fixedSize()
            }
            HStack {
                Text("Has premium: \(userStore.hasPremium ? "Yes" : "No!")")
                Button("Toggle") { userStore.hasPremium.toggle() }
            }
            HStack {
                Text("Emoji: \(emojiStore.emoji)")
                Button("Update") { emojiStore.update() }
            }
            HStack {
                Text("Count: \(count)")
                Button("+1") { count += 1 }
                Button("-1") { count -= 1 }
            }
        }
        .padding()
        .background(Rectangle().stroke(.mint, lineWidth: 1))
    }
}

// ✅ replaces `PreviewProvider`
#Preview("Parent") {
    ParentView()
}

// ✅ replaces `PreviewProvider`
#Preview("Child") {
    @Previewable @State var userStore = UserStore() // ✅ 🔗 replaces `StateObject`
    @Previewable @State var emojiStore = EmojiStore() // ✅ 🔗 replaces `StateObject`
    @Previewable @State var count = 10 // ✅ 📦 unchanged
    ChildView(emojiStore: emojiStore, count: $count)
        .environment(\.lastRefresh, .now) // ✅ 📦 unchanged
        .environment(userStore) // ✅ 🔗 replaces `.environmentObject`
}
```

And here's the same example as above, just painted with the old, outdated syntax:

```swift
// iOS 13/14/15/16
import SwiftUI

// ⛔️ 📦 replaced with `@Entry`
private struct LastRefreshKey: EnvironmentKey {
    static let defaultValue: Date = .now
}

extension EnvironmentValues {
    // ⛔️ 📦 replaced with `@Entry`
    var lastRefresh: Date {
        get { self[LastRefreshKey.self] }
        set { self[LastRefreshKey.self] = newValue }
    }
}

// ⛔️ 🔗 replaced by `@Observable`
class UserStore: ObservableObject {
    @Published var username = "max" // ⛔️ 🔗 redundant when using `@Observable`
    @Published var hasPremium = false // ⛔️ 🔗 redundant when using `@Observable`
    
    func randomize() {
        username = String((0..<3).map { _ in "abcdefghijklmnopqrstuvwxyz".randomElement()! })
    }
}

// ⛔️ 🔗 replaced by `@Observable`
class EmojiStore: ObservableObject {
    @Published var emoji = "😀" // ⛔️ 🔗 redundant when using `@Observable`
    
    func update() {
        emoji = String(UnicodeScalar(Int.random(in: 0x1F600...0x1F64F))!)
    }
}

struct ParentView: View {
    @State private var lastRefresh: Date = .now // ✅ 📦 unchanged
    @StateObject private var userStore = UserStore() // ⛔️ 🔗 replaced with `@State`
    @StateObject private var emojiStore = EmojiStore() // ⛔️ 🔗 replaced with `@State`
    @State private var count: Int = 0 // ✅ 📦 unchanged
    
    var body: some View {
        VStack(spacing: 15) {
            HStack {
                Text("Last Refresh: \(lastRefresh.formatted(date: .omitted, time: .complete))")
                Button("Refresh") { lastRefresh = .now }
            }
            HStack {
                Text("Username: \(userStore.username)")
                Button("Randomize") { userStore.randomize() }
            }
            HStack {
                Text("Has premium: \(userStore.hasPremium ? "Yes" : "No!")")
                Button("Toggle") { userStore.hasPremium.toggle() }
            }
            HStack {
                Text("Emoji: \(emojiStore.emoji)")
                Button("Update") { emojiStore.update() }
            }
            HStack {
                Text("Count: \(count)")
                Button("+1") { count += 1 }
                Button("-1") { count -= 1 }
            }
            ChildView(
                emojiStore: emojiStore, // ✅ 📦 unchanged
                count: $count // ✅ 📦 unchanged
            )
        }
        .padding()
        .background(Rectangle().stroke(Color.purple, lineWidth: 1))
        .environment(\.lastRefresh, lastRefresh) // ✅ 📦 unchanged
        .environmentObject(userStore) // ⛔️ 🔗 replaced with `.environment`
    }
}

struct ChildView: View {
    @Environment(\.lastRefresh) private var lastRefresh: Date // ✅ 📦 unchanged
    @EnvironmentObject private var userStore: UserStore // ⛔️ 🔗 replaced with `@Environment`
    @ObservedObject var emojiStore: EmojiStore // ⛔️ 🔗 replaced with `@Bindable`
    @Binding var count: Int // ✅ 📦 unchanged
    
    var body: some View {
        VStack(spacing: 15) {
            HStack {
                Text("Last Refresh: \(lastRefresh.formatted(date: .omitted, time: .complete))")
            }
            HStack {
                Text("Edit username:")
                TextField("", text: $userStore.username)
                    .textInputAutocapitalization(.never)
                    .fixedSize()
            }
            HStack {
                Text("Has premium: \(userStore.hasPremium ? "Yes" : "No!")")
                Button("Toggle") { userStore.hasPremium.toggle() }
            }
            HStack {
                Text("Emoji: \(emojiStore.emoji)")
                Button("Update") { emojiStore.update() }
            }
            HStack {
                Text("Count: \(count)")
                Button("+1") { count += 1 }
                Button("-1") { count -= 1 }
            }
        }
        .padding()
        .background(Rectangle().stroke(Color.mint, lineWidth: 1))
    }
}

// ⛔️ replaced with `#Preview`
struct ParentView_Previews: PreviewProvider {
    static var previews: some View {
        ParentView()
    }
}

// ⛔️ replaced with `#Preview`
struct ChildView_Previews: PreviewProvider {
    static var previews: some View {
        Preview()
    }
    
    struct Preview: View {
        @StateObject var userStore = UserStore() // ⛔️ 🔗 replaced with `@State`
        @StateObject var emojiStore = EmojiStore() // ⛔️ 🔗 replaced with `@State`
        @State var count: Int = 10 // ✅ 📦 unchanged
        
        var body: some View {
            ChildView(emojiStore: emojiStore, count: $count)
                .environment(\.lastRefresh, .now) // ✅ 📦 unchanged
                .environmentObject(userStore) // ⛔️ 🔗 replaced with `.environment`
        }
    }
}
```

## Between the Lines

As you can see, the two blocks of code are largely the same. The only real differences are in the reference type data flow. Thanks to Observation and `@Observable` things are a little more simple and a little better aligned with how value types have been handled since iOS 13:

**1. Source of Truth**

- 📦 `@State` 
- 🔗 `@State` *replacing `@StateObject`*

**2. Read/Write Access**

- 📦 `@Binding`
- 🔗 `@Bindable` *replacing `@ObservedObject`*

**3. Global Access**

- 📦 `@Environment`
- 🔗 `@Environment` *replacing `@EnvironmentObject`*

## Rough Edges

Observation framework is a great improvement to data flow in SwiftUI, but there are still some awkward parts. The most notable is that we need two different two-way read-write binding mechanisms (`@Binding` and `@Bindable`) instead of one unified approach. Even more frustrating is the explicit "rebinding" requirement for working with environment objects:

```swift
@Environment(UserStore.self) private var userStore
// ...
@Bindable var userStore = userStore // Required "rebinding"
```

Hopefully Apple unifies these binding mechanisms in the future, similar to how they've deftly consolidated State and Environment handling!
