---
title: SwiftUI is not UIKit
date: 2024-11-14
tags: code
slug: notuikit
---

Programming basically boils down to two fundamentals: data flow and naming things. Simple in theory, easy to complicate in practice. Let's look at some code that updates an emoji on a "parent" view from a "child" view action. 

#### Boilerplate UIKit

In UIKit it's a whole song and dance:

```swift
import UIKit

class ParentViewController: UIViewController {
    var labelText = "🐶" {
        didSet {
            label.text = "Label: \(labelText)"
            childViewController?.updateLabel(with: labelText)
        }
    }
    
    private let label = UILabel()
    private let childContainer = UIView()
    private var childViewController: ChildViewController?
    
    override func viewDidLoad() {
        super.viewDidLoad()
        setupUI()
    }
    
    private func setupUI() {
        view.backgroundColor = .white
        view.layer.borderColor = UIColor.orange.cgColor
        view.layer.borderWidth = 1
        view.layoutMargins = UIEdgeInsets(top: 10, left: 10, bottom: 10, right: 10)
        let parentStack = UIStackView(arrangedSubviews: [
          createParentLabelStack(), childContainer
        ])
        parentStack.axis = .vertical
        parentStack.spacing = 8
        parentStack.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(parentStack)
        NSLayoutConstraint.activate([
            parentStack.centerXAnchor.constraint(equalTo: view.centerXAnchor),
            parentStack.centerYAnchor.constraint(equalTo: view.centerYAnchor),
            childContainer.heightAnchor.constraint(equalToConstant: 100),
            childContainer.widthAnchor.constraint(equalToConstant: 150)
        ])
        let childVC = ChildViewController()
        childVC.labelText = labelText
        childVC.onUpdateText = { [weak self] newText in
            self?.labelText = newText
        }
        addChild(childVC)
        childContainer.addSubview(childVC.view)
        childVC.view.frame = childContainer.bounds
        childVC.didMove(toParent: self)
        childViewController = childVC
        childContainer.layoutMargins = UIEdgeInsets(
            top: 10, left: 10, bottom: 10, right: 10
        )
    }
  
    private func createParentLabelStack() -> UIView {
        let parentLabel = UILabel()
        parentLabel.text = "Parent"
        let stack = UIStackView(arrangedSubviews: [parentLabel, label])
        stack.axis = .vertical
        stack.alignment = .center
        stack.spacing = 4
        stack.layer.borderColor = UIColor.red.cgColor
        stack.layer.borderWidth = 1
        stack.layoutMargins = UIEdgeInsets(top: 10, left: 10, bottom: 10, right: 10)
        stack.isLayoutMarginsRelativeArrangement = true
        label.text = "Label: \(labelText)"
        label.textAlignment = .center
        return stack
    }
}

class ChildViewController: UIViewController {
    var labelText = "🐶" {
        didSet {
            label.text = "Label: \(labelText)"
        }
    }
    
    var onUpdateText: ((String) -> Void)?
    private let label = UILabel()
    private let updateButton = UIButton(type: .system)
    
    override func viewDidLoad() {
        super.viewDidLoad()
        setupUI()
    }
    
    private func setupUI() {
        view.layer.borderColor = UIColor.green.cgColor
        view.layer.borderWidth = 1
        view.layoutMargins = UIEdgeInsets(top: 10, left: 10, bottom: 10, right: 10)
        label.text = "Label: \(labelText)"
        label.textAlignment = .center
        updateButton.setTitle("Update", for: .normal)
        updateButton.addTarget(self, action: #selector(handleUpdateButtonTap), for: .touchUpInside)
        let childLabel = UILabel()
        childLabel.text = "Child"
        let stack = UIStackView(arrangedSubviews: [childLabel, label, updateButton])
        stack.axis = .vertical
        stack.alignment = .center
        stack.spacing = 4
        stack.translatesAutoresizingMaskIntoConstraints = false
        stack.isLayoutMarginsRelativeArrangement = true
        view.addSubview(stack)
        NSLayoutConstraint.activate([
            stack.centerXAnchor.constraint(equalTo: view.centerXAnchor),
            stack.centerYAnchor.constraint(equalTo: view.centerYAnchor)
        ])
    }
  
    @objc private func handleUpdateButtonTap() {
        labelText = "🐈"
        onUpdateText?(labelText)
    }
    
    func updateLabel(with text: String) {
        labelText = text
    }
}

// Only required for Xcode Previews
import SwiftUI

struct ParentViewControllerWrapper: UIViewControllerRepresentable {
    @Binding var text: String
    
    func makeUIViewController(context: Context) -> ParentViewController {
        let parentVC = ParentViewController()
        parentVC.labelText = text
        return parentVC
    }
    
    func updateUIViewController(_ uiViewController: ParentViewController, context: Context) {
        uiViewController.labelText = text
    }
}

#Preview {
    @Previewable @State var text = "🐶"
    ParentViewControllerWrapper(text: $text)
        .frame(width: 200, height: 220)
}
```

All of that to change an emoji from "🐶" to "🐈"!

#### "SwiftUIKit"

Many seasoned UIKit developers transitioning to SwiftUI treat the framework as “UIKit with different syntax.” The result? Bloated SwiftUI code that looks like this:

```swift
import SwiftUI

// Unnecessary coordinator pattern
class ParentCoordinator {
    // Unneccessary nesting
    weak var parentViewModel: ParentViewModel?
    var childCoordinator: ChildCoordinator?
    
    init(parentViewModel: ParentViewModel) {
        self.parentViewModel = parentViewModel
        self.childCoordinator = ChildCoordinator(childViewModel: parentViewModel.childViewModel)
        self.childCoordinator?.delegate = self
    }
}

// Unneccessary delegate pattern
extension ParentCoordinator: ChildCoordinatorDelegate {
    func childCoordinatorDidUpdateLabelText(_ newText: String) {
        parentViewModel?.labelText = newText
    }
}

// Unneccessary protocol
protocol ChildCoordinatorDelegate: AnyObject {
    func childCoordinatorDidUpdateLabelText(_ newText: String)
}

// Unneccessary child coordinator
class ChildCoordinator {
    // Unneccessary nesting
    weak var childViewModel: ChildViewModel?
    weak var delegate: ChildCoordinatorDelegate?
    
    init(childViewModel: ChildViewModel) {
        self.childViewModel = childViewModel
    }
    
    // Unnecessary @MainActor
    @MainActor func updateText() {
        childViewModel?.updateText()
        delegate?.childCoordinatorDidUpdateLabelText(childViewModel!.labelText)
    }
}

// Unneccessary view model
@Observable
class ParentViewModel {
    var labelText: String
    // Unneccessary nesting
    var childViewModel: ChildViewModel
    var coordinator: ParentCoordinator?
    
    init(labelText: String = "🐶") {
        self.labelText = labelText
        self.childViewModel = ChildViewModel(labelText: labelText)
        self.coordinator = ParentCoordinator(parentViewModel: self)
    }
}

// Unneccessary view model
@Observable
class ChildViewModel {
    var labelText: String
    
    init(labelText: String) {
        self.labelText = labelText
    }
    
    // Unneccessary @MainActor
    @MainActor func updateText() {
        labelText = "🐈"
    }
}

// Overly complex view hierarchy
struct ParentView: View {
    @Bindable var viewModel: ParentViewModel
    
    init() {
        let viewModel = ParentViewModel()
        self.viewModel = viewModel
    }
    
    var body: some View {
        VStack {
            VStack {
                Text("Parent")
                Text("Label: \(viewModel.labelText)")
            }
            .padding()
            .background(Rectangle().stroke(Color.red))
            ChildView(viewModel: viewModel.childViewModel, coordinator: viewModel.coordinator!.childCoordinator!)
        }
        .padding()
        .background(Rectangle().stroke(Color.orange))
    }
}

// Child view with direct connection to the coordinator
struct ChildView: View {
    @Bindable var viewModel: ChildViewModel
    var coordinator: ChildCoordinator
    
    var body: some View {
        VStack {
            Text("Child")
            Text("Label: \(viewModel.labelText)")
            Button(action: {
                coordinator.updateText()
            }) {
                Text("Update")
            }
        }
        .padding()
        .background(Rectangle().stroke(Color.green))
    }
}

#Preview {
    ParentView()
}
```

Coordinators, delegates, nested view models... enough boilerplate to sink a ship!

#### Vanilla SwiftUI

Here's the exact same problem solved with some vanilla SwiftUI:

```swift
import SwiftUI

struct ParentView: View {
    // Single source of truth using @State
    @State private var text = "🐶"
    
    // Simple, declarative view hierarchy
    var body: some View {
        VStack {
            VStack {
                Text("Parent")
                Text("Label: \(text)")
            }
            .padding()
            .background(Rectangle().stroke(.red))
            ChildView(text: $text)
        }
        .padding()
        .background(Rectangle().stroke(.orange))
    }
}

struct ChildView: View {
    // Direct connection to parent state using @Binding
    @Binding var text: String
    
    var body: some View {
        VStack {
            Text("Child")
            Text("Label: \(text)")
            Button {
                text = "🐈"
            } label: {
                Text("Update")
            }
        }
        .padding()
        .background(Rectangle().stroke(.green))
    }
}

#Preview {
    ParentView()
}
```

No coordinators. No delegates. No view models. Just `@State` and `@Binding` doing what they were designed to do. And letting SwiftUI handle all the complexity that had to be handled manually in UIKit.

#### MVVM

If you *must* (a topic for another time) use MVVM here's how the architecture might be used with SwiftUI:

```swift
import SwiftUI

@Observable
class ViewModel {
    // Single source of truth at the model layer
    var text = "🐶"
    
    func update() {
        text = "🐈"
    }
}

struct ParentView: View {
    // View owns the model instance
    @State var viewModel = ViewModel()
    
    var body: some View {
        VStack {
            VStack {
                Text("Parent")
                Text("Label: \(viewModel.text)")
            }
            .padding()
            .background(Rectangle().stroke(.red))
            ChildView()
        }
        .padding()
        .background(Rectangle().stroke(.orange))
        .environment(viewModel)
    }
}

struct ChildView: View {
    // Child accesses shared model through environment
    @Environment(ViewModel.self) var viewModel: ViewModel
    
    var body: some View {
        VStack {
            Text("Child")
            Text("Label: \(viewModel.text)")
            Button {
                viewModel.update()
            } label: {
                Text("Update")
            }
        }
        .padding()
        .background(Rectangle().stroke(.green))
    }
}

#Preview {
    ParentView()
}
```

At least the thing given the ViewModel name is actually a view model this time!

#### The Bottom Line

SwiftUI isn’t just a new UI framework—it’s a completely different way of thinking. A brand new way of building. UIKit patterns worked well... in UIKit. Forcing them into SwiftUI only creates complexity.

**Less code == more value.**