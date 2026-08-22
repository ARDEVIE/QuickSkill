import SwiftUI

struct ContentView: View {
    // Оставили только сохранение темной темы
    @AppStorage("isDarkMode") var isDarkMode = false
    
    var body: some View {
        TabView {
            HomeView()
                .tabItem {
                    Image(systemName: "house.fill")
                }
            
            CatalogView()
                .tabItem {
                    Image(systemName: "magnifyingglass")
                }
            
            ForumView()
                .tabItem {
                    Image(systemName: "bubble.left.and.bubble.right.fill")
                }
            
            AddCourseView()
                .tabItem {
                    Image(systemName: "plus")
                }
            
            ProfileView()
                .tabItem {
                    Image(systemName: "person.crop.circle")
                }
        }
        .accentColor(.primary)
        .preferredColorScheme(isDarkMode ? .dark : .light)
    }
}

#Preview {
    ContentView().environmentObject(AppViewModel())
}
