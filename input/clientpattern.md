---
title: The Client Pattern
date: 2024-11-20
tags: code
slug: clientpattern 
---

I recently wrapped up some work on a client project that used [TCA](https://github.com/pointfreeco/swift-composable-architecture). While I didn't love the framework, I'm thankful for the opportunity because it introduced me to something brilliant: the Client Pattern.

#### The Client Pattern
The thing I'm calling the Client Pattern is really just a simplified version of Point-Free's `DependencyClient` from their [`swift-dependencies`](https://github.com/pointfreeco/swift-dependencies) library. While the benefits are well articulated in [this blog post](https://www.pointfree.co/blog/posts/120-macro-bonanza-dependencies), you can get most of the value with just a few lines of Swift:

```swift
import Foundation

struct MyClient {
    var fetch: @Sendable (_ value: Int) async throws -> String
}

extension MyClient {
    static let live = Self(
        fetch: { value in
            // Implementation here...
            return "Fetched value: \(value)"
        }
    )
}

func fetch(with client: MyClient = .live) async throws {
    let result = try await client.fetch(1)
    print(result)
}
```

No protocols. No abstractions. No third-party dependencies to manage... dependencies. Just structs and closures to make testing downstream dead simple.

#### A "Real" Example

To demonstrate the real power of the Client Pattern, let's build a client for the [Sunrise-Sunset API](https://sunrise-sunset.org/api).

First, define the response type:

```swift
import Foundation

struct SuntimesResponse: Decodable {
    let results: Results
    
    struct Results: Decodable {
        let sunrise: Date
        let sunset: Date
        
        enum CodingKeys: String, CodingKey {
            case sunrise
            case sunset
        }
    }
}
```

Then create the client interface:

```swift
struct SuntimesClient {
    var fetchSunrise: @Sendable (_ latitude: Double, _ longitude: Double) async throws -> Date
    var fetchSunset: @Sendable (_ latitude: Double, _ longitude: Double) async throws -> Date
}
```

Extend the client with a `.live` implementation (to do the actual networking):

```swift
extension SuntimesClient {
    static let live = Self(
        fetchSunrise: { latitude, longitude in
            let result = try await Self.fetchSuntimes(latitude: latitude, longitude: longitude)
            return result.sunrise
        },
        fetchSunset: { latitude, longitude in
            let result = try await Self.fetchSuntimes(latitude: latitude, longitude: longitude)
            return result.sunset
        }
    )
  
    private static func fetchSuntimes(latitude: Double, longitude: Double) async throws -> SuntimesResponse.Results {
        var components = URLComponents(string: "https://api.sunrise-sunset.org/json")
        components?.queryItems = [
            URLQueryItem(name: "lat", value: "\(latitude)"),
            URLQueryItem(name: "lng", value: "\(longitude)"),
            URLQueryItem(name: "formatted", value: "0")
        ]
        guard let url = components?.url else { throw URLError(.badURL) }
        let (data, _) = try await URLSession.shared.data(from: url)
        let decoder = JSONDecoder()
        decoder.dateDecodingStrategy = .iso8601
        let response = try decoder.decode(SuntimesResponse.self, from: data)
        return response.results
    }
}
```
Use the `@Entry` macro to inject the `.live` implementation into the SwiftUI environment:

```swift
import SwiftUI

extension EnvironmentValues {
    @Entry var suntimesClient: SuntimesClient = .live
}
```

And create a view that picks up the injected client:

```swift
struct SuntimesClientView: View {
    @Environment(\.suntimesClient) var client: SuntimesClient
    @State var sunset: Date?
    
    var body: some View {
        VStack {
            Text(sunset?.formatted() ?? "")
            Button("Fetch Sunset") {
                Task { await fetchSunset() }
            }
        }
    }
  
    private func fetchSunset() async {
        do {
            sunset = try await client.fetchSunset(43.6532, -79.3832)
        } catch {
            print(error)
        }
    }
}

#Preview {
    SuntimesClientView()
}
```

With the Client Pattern in place, testing and previews become incredibly simple. Just define a mock client:

```swift
extension SuntimesClient {
    static let preview = Self(
        fetchSunrise: { _, _ in throw URLError(.badServerResponse) }, // Simulates an error
        fetchSunset: { _, _ in .now } // Returns the current time for sunset
    )
}
```

And inject it into previews:

```swift
#Preview("Client Pattern (Mock)") {
    SuntimesClientView()
        .environment(\.suntimesClient, .preview) // Injects mock client
}
```

#### Copy-and-paste

Here's all of the code in a single block that you can copy-and-paste directly into Xcode to try out the Client Pattern for yourself:

```swift
import SwiftUI

struct SuntimesResponse: Decodable {
    let results: Results
    
    struct Results: Decodable {
        let sunrise: Date
        let sunset: Date
        
        enum CodingKeys: String, CodingKey {
            case sunrise
            case sunset
        }
    }
}

// MARK: - Client Definition
// Provides async closures for fetching sunrise and sunset data (Swift 6 ready!)
struct SuntimesClient {
    var fetchSunrise: @Sendable (_ latitude: Double, _ longitude: Double) async throws -> Date
    var fetchSunset: @Sendable (_ latitude: Double, _ longitude: Double) async throws -> Date
}

// MARK: - Live Implementation
// Implements live API calls for sunrise and sunset
extension SuntimesClient {
    static let live = Self(
        fetchSunrise: { latitude, longitude in
            let result = try await Self.fetchSuntimes(latitude: latitude, longitude: longitude)
            return result.sunrise
        },
        fetchSunset: { latitude, longitude in
            let result = try await Self.fetchSuntimes(latitude: latitude, longitude: longitude)
            return result.sunset
        }
    )
    
    // Helper: Makes the API call to retrieve sunrise and sunset data
    private static func fetchSuntimes(latitude: Double, longitude: Double) async throws -> SuntimesResponse.Results {
        var components = URLComponents(string: "https://api.sunrise-sunset.org/json")
        components?.queryItems = [
            URLQueryItem(name: "lat", value: "\(latitude)"),
            URLQueryItem(name: "lng", value: "\(longitude)"),
            URLQueryItem(name: "formatted", value: "0")
        ]
        guard let url = components?.url else { throw URLError(.badURL) }
        let (data, _) = try await URLSession.shared.data(from: url)
        let decoder = JSONDecoder()
        decoder.dateDecodingStrategy = .iso8601
        let response = try decoder.decode(SuntimesResponse.self, from: data)
        return response.results
    }
}

// MARK: - Preview Implementation
// Simulates sunrise and sunset fetching for previews and testing
extension SuntimesClient {
    static let preview = Self(
        fetchSunrise: { _, _ in throw URLError(.badServerResponse) }, // Simulates an error
        fetchSunset: { _, _ in .now } // Returns the current time for sunset
    )
}

// MARK: - Environment Values Extension
// Adds `@Environment(\.suntimesClient) var suntimesClient` to the SwiftUI environment (default to .live)
extension EnvironmentValues {
    @Entry var suntimesClient: SuntimesClient = .live
}

struct SuntimesClientView: View {
    @Environment(\.suntimesClient) var client: SuntimesClient
    @State var sunset: Date?
    
    var body: some View {
        VStack {
            Text(sunset?.formatted() ?? "")
            Button("Fetch Sunset") {
                Task { await fetchSunset() }
            }
        }
    }
    
    // Fetches sunset data asynchronously and updates the state
    private func fetchSunset() async {
        do {
            sunset = try await client.fetchSunset(43.6532, -79.3832)
        } catch {
            print(error)
        }
    }
}

// MARK: - Previews
#Preview("Client Pattern (Live)") {
    SuntimesClientView()
}

#Preview("Client Pattern (Mock)") {
    SuntimesClientView()
        .environment(\.suntimesClient, .preview) // Injects mock client
}
```
#### The Old Way (Don't Do This)

For comparison, here's the protocol-based [Service Pattern](https://medium.com/livefront/creating-a-service-layer-in-swift-ea771088fb66) I've previously used for app networking:

```swift
import SwiftUI
import Foundation

// MARK: - Protocol Definition
// Enables mocking and testing of sunrise/sunset fetching
protocol SuntimesServiceable {
    func fetchSunrise(latitude: Double, longitude: Double) async throws -> Date
    func fetchSunset(latitude: Double, longitude: Double) async throws -> Date
}

// MARK: - Live Service Implementation
// Implements the SuntimesServiceable protocol for actual API calls
struct SuntimesService: SuntimesServiceable {
    func fetchSunrise(latitude: Double, longitude: Double) async throws -> Date {
        let results = try await fetchSuntimes(latitude: latitude, longitude: longitude)
        return results.sunrise
    }
    
    func fetchSunset(latitude: Double, longitude: Double) async throws -> Date {
        let results = try await fetchSuntimes(latitude: latitude, longitude: longitude)
        return results.sunset
    }
    
    // Helper: Makes the API call to retrieve sunrise and sunset data
    private func fetchSuntimes(latitude: Double, longitude: Double) async throws -> SuntimesResponse.Results {
        var components = URLComponents(string: "https://api.sunrise-sunset.org/json")
        components?.queryItems = [
            URLQueryItem(name: "lat", value: "\(latitude)"),
            URLQueryItem(name: "lng", value: "\(longitude)"),
            URLQueryItem(name: "formatted", value: "0")
        ]
        guard let url = components?.url else { throw URLError(.badURL) }
        let (data, _) = try await URLSession.shared.data(from: url)
        let decoder = JSONDecoder()
        decoder.dateDecodingStrategy = .iso8601
        let response = try decoder.decode(SuntimesResponse.self, from: data)
        return response.results
    }
}

// MARK: - Mock Service for Testing
// Provides predictable behavior for testing without actual API calls
struct MockSuntimesService: SuntimesServiceable {
    func fetchSunrise(latitude: Double, longitude: Double) async throws -> Date {
        .now // Returns the current time for sunrise
    }
    
    func fetchSunset(latitude: Double, longitude: Double) async throws -> Date {
        throw URLError(.badServerResponse) // Simulates an error
    }
}

struct SuntimesServiceView: View {
    @State var sunrise: Date?
    private let service: SuntimesServiceable
    
    // Injects the dependency, defaulting to the live service
    init(service: SuntimesServiceable = SuntimesService()) {
        self.service = service
    }
    
    var body: some View {
        VStack {
            Text(sunrise?.formatted() ?? "")
            Button("Fetch Sunrise") {
                Task { await fetchSunrise() }
            }
        }
    }
    
    // Fetches sunrise data asynchronously
    private func fetchSunrise() async {
        do {
            // Warning: Swift 6 Error (Sending 'self.service' risks causing data races)
            // Sending main actor-isolated 'self.service' to nonisolated instance method 'fetchSunrise(latitude:longitude:)' risks causing data races between nonisolated and main actor-isolated uses
            sunrise = try await service.fetchSunrise(latitude: 43.6532, longitude: -79.3832)
        } catch {
            print(error)
        }
    }
}

// MARK: - Previews
#Preview("Service Pattern (Live)") {
    SuntimesServiceView(service: SuntimesService())
}

#Preview("Service Pattern (Preview)") {
    SuntimesServiceView(service: MockSuntimesService())
}
```

#### Keeping It Simple

For me, I love the the Client Pattern over the Service Pattern because it:

- Removes protocol overhead
- Makes testing easier with closures 
- Integrates well with SwiftUI
- And requires less code

I'm excited to use the pattern going forward because it leverages the best parts of Swift/SwiftUI and helps to keep my code as simple as possible!
