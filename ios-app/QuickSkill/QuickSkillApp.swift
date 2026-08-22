import SwiftUI

@main
struct QuickSkillApp: App {
    @AppStorage("isLoggedIn") var isLoggedIn = false
    
    // Создаем единственный экземпляр нашей логики на всё приложение
    @StateObject private var viewModel = AppViewModel()
    
    var body: some Scene {
        WindowGroup {
            if isLoggedIn {
                ContentView()
                    // Передаем viewModel вниз по иерархии
                    .environmentObject(viewModel)
            } else {
                AuthView()
            }
        }
    }
}
