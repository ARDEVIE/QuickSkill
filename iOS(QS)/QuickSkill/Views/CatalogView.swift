import SwiftUI

struct CatalogView: View {
    @State private var searchText = ""
    
    var body: some View {
        NavigationView {
            VStack {
                // Поисковая строка
                HStack {
                    Image(systemName: "magnifyingglass")
                        .foregroundColor(.secondary)
                    TextField("Искать навыки и курсы...", text: $searchText)
                }
                .padding()
                .background(Color(UIColor.secondarySystemBackground))
                .cornerRadius(16)
                .padding()
                
                Spacer()
                
                // Заглушка, когда ничего не ищут
                VStack(spacing: 12) {
                    Image(systemName: "books.vertical.fill")
                        .font(.system(size: 60))
                        .foregroundColor(Color(UIColor.systemGray4))
                    Text("Введите название темы")
                        .font(.headline)
                    Text("Здесь появятся результаты поиска")
                        .font(.subheadline)
                        .foregroundColor(.secondary)
                }
                
                Spacer()
            }
            .navigationTitle("Каталог")
            .background(Color(UIColor.systemBackground))
        }
    }
}

#Preview {
    CatalogView()
}
