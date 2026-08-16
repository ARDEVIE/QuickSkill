import SwiftUI

struct FavoritesView: View {
    var body: some View {
        NavigationView {
            ScrollView(showsIndicators: false) {
                VStack(alignment: .leading, spacing: 20) {
                    
                    Text("Избранное")
                        .font(.largeTitle)
                        .fontWeight(.bold)
                        .padding(.horizontal)
                        .padding(.top, 10)
                    
                    VStack(spacing: 16) {
                        // Имитация сохраненных курсов
                        ForEach(0..<3, id: \.self) { _ in
                            CourseRowView()
                        }
                    }
                    .padding(.horizontal)
                    
                }
                .padding(.bottom, 20)
            }
            .navigationBarHidden(true)
            .background(Color(UIColor.systemBackground))
        }
    }
}

#Preview {
    Group {
        FavoritesView().preferredColorScheme(.light)
        FavoritesView().preferredColorScheme(.dark)
    }
}
