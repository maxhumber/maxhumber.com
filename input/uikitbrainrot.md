---
title: UIKit Brain Rot
date: 2024-11-14
tags: code,swift
slug: uikitbrainrot
---

This is your brain on UIKit:

```swift
import SwiftUI

class ParentCoordinator {
    weak var parentViewModel: ParentViewModel?
    var childCoordinator: ChildCoordinator?

    init(parentViewModel: ParentViewModel) {
        self.parentViewModel = parentViewModel
        self.childCoordinator = ChildCoordinator(childViewModel: parentViewModel.childViewModel)
        self.childCoordinator?.delegate = self
    }
}

extension ParentCoordinator: ChildCoordinatorDelegate {
    func childCoordinatorDidUpdateLabelText(_ newText: String) {
        parentViewModel?.labelText = newText
    }
}

protocol ChildCoordinatorDelegate: AnyObject {
    func childCoordinatorDidUpdateLabelText(_ newText: String)
}

class ChildCoordinator {
    weak var childViewModel: ChildViewModel?
    weak var delegate: ChildCoordinatorDelegate?

    init(childViewModel: ChildViewModel) {
        self.childViewModel = childViewModel
    }

    @MainActor func updateText() {
        childViewModel?.updateText()
        delegate?.childCoordinatorDidUpdateLabelText(childViewModel!.labelText)
    }
}

@Observable
class ParentViewModel {
    var labelText: String
    var childViewModel: ChildViewModel
    var coordinator: ParentCoordinator?

    init(labelText: String = "🐶") {
        self.labelText = labelText
        self.childViewModel = ChildViewModel(labelText: labelText)
        self.coordinator = ParentCoordinator(parentViewModel: self)
    }
}


@Observable
class ChildViewModel {
    var labelText: String

    init(labelText: String) {
        self.labelText = labelText
    }

    @MainActor func updateText() {
        labelText = "🐈"
    }
}

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

Don't ever smoke UIKit!