plugins {
    id("dev.nx.gradle.project-graph").version("0.1.20")
}

allprojects {
    apply {
        plugin("dev.nx.gradle.project-graph")
    }
}
