import com.github.davidmc24.gradle.plugin.avro.GenerateAvroJavaTask
import dev.nx.gradle.nx

nx {
    set("name", "aurelius-java-example")
}

plugins {
    id("com.github.davidmc24.gradle.plugin.avro").version("1.9.1")
}

repositories {
    gradlePluginPortal()
}

dependencies {
    implementation(libs.avro)
}

java {
    toolchain {
        languageVersion = JavaLanguageVersion.of(21)
    }
}

tasks.named<Test>("test") {
    useJUnitPlatform()
}

allprojects {
    apply {
        plugin("project-report")
    }
}

tasks.register<GenerateAvroJavaTask>("generateAvro") {
    source("../../../schemas/avro")
    setOutputDir(file("src/main/java"))
}

tasks.register("projectReportAll") {
    allprojects.forEach {
        dependsOn(it.tasks.getAt("projectReport"))
    }

    gradle.includedBuilds.forEach {
        dependsOn(it.task(":projectReportAll"))
    }
}
