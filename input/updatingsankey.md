---
title: Updating Sankey
date: 2024-12-04
tags: code,swift
slug: updatingsankey
---

Just released [Sankey 2.0](https://github.com/maxhumber/Sankey/tree/2.0), an open-source package for building Sankey diagrams in SwiftUI.

#### What?

A Sankey diagram visualizes flow: where stuff is coming from, where it's going, and how much stuff is moving. Thick and thin bands represent the volume of flow. Sankey diagrams are perfect for showing money, user behavior, energy usage—basically anything involving inputs, outputs, and the in-between.

#### Why + What's New?

I originally built [Sankey 1.0](https://github.com/maxhumber/Sankey/tree/1.0) in May 2022 for a contract project (no other options existed at the time). Then I forgot about it—until a couple of weeks ago when I needed a Sankey diagram for a new app.

This new project requires offline rendering and Dark Mode support. So, while adding these features to Sankey, I also streamlined the API to make it dead simple to create beautiful charts like this:

![](https://github.com/maxhumber/Sankey/raw/master/Images/quick.png)

With code that is a simple as this:

```swift
import Sankey
import SwiftUI

struct ContentView: View {
    let data = SankeyData(
        nodes: [
            SankeyNode("A", color: .blue),
            SankeyNode("B", color: .purple),
            SankeyNode("X", color: .red),
            SankeyNode("Y", color: .yellow),
            SankeyNode("Z", color: .green),
        ],
        links: [
            SankeyLink(5, from: "A", to: "X"),
            SankeyLink(7, from: "A", to: "Y"),
            SankeyLink(6, from: "A", to: "Z"),
            SankeyLink(2, from: "B", to: "X"),
            SankeyLink(9, from: "B", to: "Y"),
            SankeyLink(4, from: "B", to: "Z"),
        ]
    )
    
    var body: some View {
        SankeyDiagram(data)
            .nodeOpacity(0.9)
            .linkColorMode(.gradient)
            .padding(10)
            .frame(height: 350)
    }
}

#Preview {
    ContentView()
}
```

#### All "Old" Code is "Bad" Code

![](https://i.redd.it/djajn2o19ca81.jpg)

Revisiting old code is always a fun (and humbling) exercise. Because the code in 1.0 was bad! (If you're not embarrassed by your past work, are you even learning?)

While the core feature of Sankey—connecting source nodes to target nodes— remains 90% of the code in 2.0 is new. Mostly, this is a consequence of replacing the [Google Charts](https://developers.google.com/chart) rendering engine with [D3.js](https://d3js.org/). But also because I removed a lot of the over-engineered "organization", limited excessive configuration options, and fixed a lot of color handling mistakes.

Despite these major changes, I was able to maintain a good bit of backwards compatibility (the original Quickstart still works)!

#### Too Much Structure! 

The Sankey package *should* be simple. It's just a `SankeyDiagram` SwiftUI component. And a few other structs that help in its construction. In 1.0, I went overboard trying to organize everything for "future extensibility", creating this convoluted mess:

```
--Package.swift
--Sources
----Sankey/
------Options/
--------Tooltip/
----------TextStyle/
------------SankeyOptions.Tooltip.TextStyle.swift
----------SankeyOptions.Tooltip.swift
--------Sankey/
----------SankeyOptions.Sankey.swift
----------Link/
------------Color/
--------------SankeyOptions.Sankey.Link.Color.swift
------------SankeyOptions.Sankey.Link.swift
------------ColorMode/
--------------SankeyOptions.Sankey.Link.ColorMode.swift
----------Node/
------------Label/
--------------SankeyOptions.Sankey.Node.Label.swift
------------ColorMode/
--------------SankeyOptions.Sankey.Node.ColorMode.swift
------------SankeyOptions.Sankey.Node.swift
--------SankeyOptions.swift
--------SankeyOptions+CustomStringConvertible.swift
--------SankeyOptions+init.swift
------Diagram/
--------SankeyDiagram.swift
--------SankeyDiagram+init.swift
------Link/
--------SankeyLink.swift
--------SankeyLink+ExpressibleByArrayLiteral.swift
--------SankeyLink+CustomStringConvertible.swift
------Node/
--------SankeyNode.swift
```

Now that we're in "the future" I can say that all this "organization" wasn't just unhelpful—it actively hindered my ability add to and update the package! For 2.0, I streamlined as much as possible:

```
--Package.swift
--Sources/
----Deprecated/
------SankeyDiagram+deprecated.swift
------SankeyLink+deprecated.swift
----Helpers/
------Color+.swift
------HexColor.swift
----Resources/
------d3.min.js
------d3-sankey.min.js
----SankeyData.swift
----SankeyDiagram.swift
----SankeyLink.swift
----SankeyNode.swift
----SankeyOptions.swift
----SankeyResources.swift
```

Easier to work with. But more importantly, easier to delete! Because, let's be honest—future me will probably throw it all out in another two years!

#### "WWAD"

While the original "structure" slowed me down, exposing too many configuration options to users was an even bigger mistake. Look at this old init signature:

```swift
SankeyDiagram(
    _ data: [SankeyLink],
    nodeColors: [String]? = nil,
    nodeColorMode: SankeyOptions.Sankey.Node.ColorMode = .unique,
    nodeWidth: Double? = nil,
    nodePadding: Double? = nil,
    nodeLabelColor: String = "black",
    nodeLabelFontSize: Double = 24,
    nodeLabelFontName: String? = nil,
    nodeLabelBold: Bool = false,
    nodeLabelItalic: Bool = false,
    nodeLabelPadding: Double? = nil,
    nodeInteractivity: Bool = false,
    linkColors: [String]? = nil,
    linkColorMode: SankeyOptions.Sankey.Link.ColorMode? = nil,
    linkColorFill: String? = nil,
    linkColorFillOpacity: Double? = nil,
    linkColorStroke: String? = nil,
    linkColorStrokeWidth: Double = 0,
    tooltipValueLabel: String = "",
    tooltipTextColor: String = "black",
    tooltipTextFontSize: Double = 24,
    tooltipTextFontName: String? = nil,
    tooltipTextBold: Bool = false,
    tooltipTextItalic: Bool = false,
    layoutIterations: Int = 32
) 
```

Can you tell I was just blindly trying to recreating someone else's API?

Now when I build for SwiftUI I typically ask myself: "What Would Apple Do?" (WWAD). If this piece of code were native Apple component, what would it look and feel like? I must say, I think I nailed it in 2.0:

```swift
SankeyDiagram(data)
    .nodeAlignment(.justify)
    .nodeWidth(15)
    .nodePadding(20)
    .nodeDefaultColor(.gray)
    .nodeOpacity(0.8)
    .linkDefaultColor(.gray)
    .linkOpacity(0.7)
    .linkColorMode(nil)
    .labelPadding(8)
    .labelColor(.primary)
    .labelOpacity(0.9)
    .labelFontSize(14)
    .labelFontFamily("Times")
```

All customization options are now exposed as "Modifiers" on the SankeyDiagram object itself. This is enabled by hiding the SankeyOptions struct from the user and exposing modifiers that look like this:

```swift
// ...
public func nodeOpacity(_ value: Double) -> SankeyDiagram {
    var new = self
    new.options.nodeOpacity = value
    return new
}
// ...
```

I also replaced all externally facing hex codes with native SwiftUI colors. While implementing this was complex, I thought it was better to handle the complexity myself than burden users with it. Now Dark Mode and using a "color" like `Color.primary` will just work! 

#### Conclusion

The code in Sankey 2.0 is easier to read, use, and built to be thrown away! While it's not perfect—future me will probably laugh at it in the future—it works well today. And that's all that matters. If you need to visualize flows in any of your apps I hope you give it a try!
