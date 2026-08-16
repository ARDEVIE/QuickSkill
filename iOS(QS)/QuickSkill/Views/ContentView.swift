import SwiftUI

struct ContentView: View {
    var body: some View {
        TabView {
            // 1. Главная
            HomeView()
                .tabItem {
                    Image(systemName: "house.fill")
                }
            
            // 2. Каталог
            CatalogView()
                .tabItem {
                    Image(systemName: "magnifyingglass")
                }
            
            // 3. Избранное
            FavoritesView()
                .tabItem {
                    Image(systemName: "heart") // Используем иконку сердечка
                }
            
            // 4. Добавить курс
            AddCourseView()
                .tabItem {
                    Image(systemName: "plus")
                }
            
            // 5. Профиль
            ProfileView()
                .tabItem {
                    Image(systemName: "person.crop.circle")
                }
        }
        .accentColor(.primary) // Адаптивный цвет (черный днем, белый ночью)
    }
}

// Временные заглушки для новых экранов, чтобы код скомпилировался без ошибок.
// Чуть позже мы разнесем их по отдельным файлам в папку Views.






#Preview {
    ContentView()
}
