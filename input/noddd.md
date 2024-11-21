---
title: Just Say No to DDD
date: 2024-11-19
tags: code
slug: noddd
---

Domain-driven Design (DDD) is a software design approach that attempts to structure code to "match a domain". It promises "adaptable", "scalable", and "maintainable" software by dividing apps into "bounded contexts" and by "aligning code" with "business needs". It *sounds* great, in theory. But in reality, it's a trap... especially when applied to SwiftUI.

#### Code as a Liability

Code isn't an asset. It's a liability. Every line of code is another line to test, debug, and maintain. And every line of code introduces new opportunities for new bugs. Despite the promises, DDD increases this liability by adding layers of unnecessary code and generally making a mess of everything. 

#### Broken Promises

DDD might be okay for massive, legacy, enterprise Java systems from the early aughts. But it's overkill for modern SwiftUI apps. Positioned as a way to make code adaptable, scalable, and maintainable, DDD simply fails on all three fronts:

- **Not Adaptable** - DDD makes even small changes slow and tedious. Features that should take minutes can take days because changes because every layer must be re-adjusted and re-aligned.

- **Not Scalable** - Client-side apps don't face the same scalability challenges as backend systems. DDD's attempt to "scale for the future" just ends up adding unnecessary cruft. 
- **Not Maintainable** - DDD buries logic under so many abstractions that understanding or updating code becomes a chore. Instead of simplifying maintenance, it creates friction and confusion.

#### Code Comparison

Instead of me just telling you that DDD is bad, let me show you... Consider this vanilla implementation for fetching and displaying Todos using the [jsonplaceholder](https://jsonplaceholder.typicode.com/todos/) API:

```swift
import SwiftUI

// 1. Model

struct Todo: Codable, Identifiable {
    let id: Int
    let title: String
    let completed: Bool
}

// 2. Client (fetch todos)

struct TodoClient {
    var fetchTodos: @Sendable () async throws -> [Todo]
    
    static let live = Self(
        fetchTodos: {
            guard let url = URL(string: "https://jsonplaceholder.typicode.com/todos/") else { throw URLError(.badURL) }
            let (data, _) = try await URLSession.shared.data(from: url)
            let todos = try JSONDecoder().decode([Todo].self, from: data)
            return todos
        }
    )
}

// 3. View (display todos, handle errors)

struct TodoView: View {
    @State var todos: [Todo] = []
    @State var errorMessage: String? = nil
    private let client: TodoClient = .live
    
    var body: some View {
        List {
            ForEach(todos) { todo in
                HStack {
                    Image(systemName: todo.completed ? "checkmark.circle": "circle")
                        .foregroundStyle(todo.completed ? .green : .gray)
                    Text("\(todo.title)")
                }
            }
        }
        .navigationTitle("Todo List")
        .task { await fetch() }
        .alert("Error", isPresented: .constant(errorMessage != nil)) {
            Button("OK", role: .cancel) { errorMessage = nil }
        } message: {
            Text(errorMessage ?? "No Error")
        }
    }
    
    func fetch() async {
        do {
            todos = try await client.fetchTodos()
        } catch {
            errorMessage = error.localizedDescription
        }
    }
}

#Preview {
    NavigationStack {
        TodoView()
    }
}
```

**Full DDD**

And here's what the same code might look like when you go "full DDD" (based on [this popular Medium article](https://paulallies.medium.com/clean-architecture-in-the-flavour-of-swiftui-5-5-8430786a83)). Honestly, don't even try to read or understand all of it. Just notice that it's wayyyyyy more code: 

```swift
import SwiftUI

// 1. Models
// TodoDTO: The raw data from the API
// TodoDMO: A "cleaned-up" version of the data for actual app use

struct TodoDTO: Codable {
    let id: Int
    let title: String
    let completed: Bool
    
    func toDomainModelObject() -> TodoDMO {
        TodoDMO(id: id, label: title, isCompleted: completed)
    }
}

struct TodoDMO: Identifiable {
    let id: Int
    let label: String
    let isCompleted: Bool
}

// 2. "Data Source"
// Fetches TodoDTOs from an API, making things more complicated than they need to be

protocol TodoDataSource {
    func fetchTodos() async throws -> [TodoDTO]
}

enum TodoDataSourceError: Error {
    case badUrl
    case requestError
    case decodingError
    case statusNotOK
}

struct TodoDataSourceImplementation: TodoDataSource {
    func fetchTodos() async throws -> [TodoDTO] {
        let urlString = "https://jsonplaceholder.typicode.com/todos/"
        guard let url = URL(string: urlString) else {
            throw TodoDataSourceError.badUrl
        }
        guard let (data, response) = try? await URLSession.shared.data(from: url) else {
            throw TodoDataSourceError.requestError
        }
        guard let httpResponse = response as? HTTPURLResponse, httpResponse.statusCode == 200 else {
            throw TodoDataSourceError.statusNotOK
        }
        guard let todos = try? JSONDecoder().decode([TodoDTO].self, from: data) else {
            throw TodoDataSourceError.decodingError
        }
        return todos
    }
}

// 3. "Repository"
// Converts TodoDTOs to TodoDMOs while adding an extra layer for no obvious reason

protocol TodoRepository {
    func fetchTodos() async throws -> [TodoDMO]
}

enum TodoRepositoryError: Error {
    case decodingError
    case networkError
}

struct TodoRepositoryImplementation: TodoRepository {
    private let dataSource: TodoDataSource
    
    init(dataSource: TodoDataSource) {
        self.dataSource = dataSource
    }
    
    func fetchTodos() async throws -> [TodoDMO] {
        do {
            let todosDTO = try await dataSource.fetchTodos()
            return todosDTO.map { $0.toDomainModelObject() }
        } catch TodoDataSourceError.decodingError {
            throw TodoRepositoryError.decodingError
        } catch {
            throw TodoRepositoryError.networkError
        }
    }
}

// 4. "UseCase"
// A glorified wrapper to call the repository and handle errors in a slightly different way

protocol TodoGetUseCase {
    func execute() async -> Result<[TodoDMO], TodoGetUseCaseError>
}

enum TodoGetUseCaseError: Error {
    case networkError
    case decodingError
}

struct TodoGetUseCaseImplementation: TodoGetUseCase {
    private let repository: TodoRepository
    
    init(repository: TodoRepository) {
        self.repository = repository
    }
    
    func execute() async -> Result<[TodoDMO], TodoGetUseCaseError> {
        do {
            let todos = try await repository.fetchTodos()
            return .success(todos)
        } catch {
            return .failure(error is TodoRepositoryError ? .decodingError : .networkError)
        }
    }
}

// 5. "ViewModel"
// Mediates between the UseCase and the View, because we always need more layers!

@Observable
class TodoListViewModel {
    var todos: [TodoDMO] = []
    var errorMessage = ""
    var hasError = false
    
    private let useCase: TodoGetUseCase
    
    init(useCase: TodoGetUseCase) {
        self.useCase = useCase
    }
    
    func loadTodos() async {
        errorMessage = ""
        hasError = false
        let result = await useCase.execute()
        switch result {
        case .success(let todos):
            self.todos = todos
        case .failure(let error):
            self.todos = []
            errorMessage = error.localizedDescription
            hasError = true
        }
    }
}

// 6. View
// Finally, something useful: displays todos and errors, cleaning up after all the other layers

struct DDDTodoView: View {
    @Bindable var viewModel: TodoListViewModel
    
    init(viewModel: TodoListViewModel) {
        self.viewModel = viewModel
    }
    
    var body: some View {
        List {
            ForEach(viewModel.todos) { todo in
                HStack {
                    Image(systemName: todo.isCompleted ? "checkmark.circle" : "circle")
                        .foregroundColor(todo.isCompleted ? .green : .gray)
                    Text(todo.label)
                }
            }
        }
        .navigationTitle("Todo List")
        .task { await viewModel.loadTodos() }
        .alert("Error", isPresented: $viewModel.hasError) {
            Button("OK", role: .cancel) {}
        } message: {
            Text(viewModel.errorMessage)
        }
    }
}

#Preview {
    @Previewable @State var viewModel = TodoListViewModel(
        useCase: TodoGetUseCaseImplementation(
            repository: TodoRepositoryImplementation(
                dataSource: TodoDataSourceImplementation()
            )
        ))
    NavigationView {
        DDDTodoView(viewModel: viewModel)
    }
}
```

Both implementations do **the exact same thing**! Seriously, copy-and-paste both blocks into Xcode and see for yourself! All the extra layers—the repository, use case, and view model—add **bloat without benefit.** But what about testing? Okay. Fair. To test the vanilla version, just create a `TodoClient.mock` extension and inject it where needed. Done.

#### HackerNews

If the code comparison isn't enough to convince you that DDD is unnecessary and actively counterproductive, these collected quotes from various HackerNews threads should:

> "In my 22 years of career in software starting as a developer, I have seen DDD used only one time successfully and appropriately. All other attempts were **half-baked** and **over-engineered messes**. The problem was that over several years, it was **hard to get new hires up to speed** to maintain the **complex code** and test it."

> "DDD strikes me as the software version of Agile sometimes. The ideas and philosophy behind are good, but end up being taken as a silver bullet. I’ve seen DDD being branded together with CQRS as 'Clean Architecture,' which in reality turns out to be a **mess of layers and separations**."

>  "We use DDD at the current company I work in, and to be honest, **I detest it so much** that sometimes it **makes me wonder if I even want to continue in the programming space** (been at it for 20 years). Don’t get me wrong, DDD has meaning and purpose, but some companies are applying it as a badge to be obtained instead of pondering the question: Do you really need to rewrite everything following DDD?"

>  "DDD seems to be one of those things where 'what it’s meant to mean' is very different from 'how it’s actually practiced.' Reading about what it’s meant to mean, it seems pretty common sense. As often implemented, however, it seems to lead to **a lot of accidental complexity** and **a bunch of dubious usefulness abstraction layers**."

> "In my experience, the most useful part of DDD is to have a common vocabulary for your projects—developers and end users should have some common terminology. For complex business domains, it is good to have a glossary and for your code to always use those words in the same way the business uses them. Other than that, **most DDD concepts are a bit dated, and really oriented around JAVA/C# in the early 2000s.**"

>  "All principles help you to model your software in a way that’s highly cohesive and loosely coupled. My suggestion: Stay away from all these design patterns. In my experience, they lead to **overly complex code** because of all the structure. **The best structure is the most simple**."

> "I thought the DDD hype had died down a bit, but I guess not. Eric Evans (inventor of DDD) has said in recent years that, unfortunately, once a team is big enough, all the invisible conceptual boundaries between domains blur and disappear. **People do NOT have the discipline to do DDD correctly.**"

>  "When you start thinking in abstractions and create abstractions in your code, either top-down or bottom-up, you will end up producing a good software design. This, to me, is the most untrue statement you could make about software. **Abstractions introduce more complexity**. **The more complex, the less stable and maintainable your software becomes**."

> "**Domain-Driven Design is a poison**. The book is one of the most poorly written technical books out there. There are a handful of good ideas buried in the 1,000-page unedited verbose rambling slog. The whole book should only have been 10 pages. Besides Eric Evans’s inability to write, the poison of DDD comes from locking in businesses/domain concepts into your core technology, making them inflexible and making it difficult for the business to iterate on new ideas."

> "The biggest flaw of DDD I’ve run into is there’s no emphasis on when not to use it. There’s no mention that over-coding business rules into modules and services **locks you into business processes that are slow or impossible to update**. There’s no mention that most times you want to build services that offer platform capabilities, not focus on what 'domain' they fall into. Never mind that 'domain' is basically undefined and can mean many different concepts and different types of concepts."

#### Go for Simple

SwiftUI thrives on simplicity. Not endless layers of abstractions. Instead of wasting time on "domains", "repositories", and "use cases". Let's focus on delivering features quickly with less code.