import SwiftUI

@main
struct QuickSkillApp: App {
    // Эта переменная будет храниться в памяти телефона.
    // По умолчанию пользователь не авторизован (false)
    @AppStorage("isLoggedIn") var isLoggedIn = false
    
    var body: some Scene {
        WindowGroup {
            // Проверяем статус:
            if isLoggedIn {
                // Если вошел — показываем главное меню (TabBar)
                ContentView()
            } else {
                // Если не вошел — показываем экран авторизации
                AuthView()
            }
        }
    }
}
