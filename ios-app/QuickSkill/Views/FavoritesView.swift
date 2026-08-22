import SwiftUI

struct FavoritesView: View {
    @EnvironmentObject var viewModel: AppViewModel
    
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
                        // ФИЛЬТРУЕМ ТОЛЬКО ЛАЙКНУТЫЕ КУРСЫ
                        let favCourses = viewModel.courses.filter { $0.isFavorite }
                        
                        if favCourses.isEmpty {
                            Text("Здесь пока пусто. Вы можете добавить курсы в избранное на экране деталей курса.")
                                .foregroundColor(.gray)
                                .multilineTextAlignment(.center)
                                .padding(.top, 50)
                        } else {
                            ForEach(favCourses) { course in
                                NavigationLink(destination: CourseDetailView(course: course)) {
                                    CourseRowView(course: course)
                                }
                                .buttonStyle(PlainButtonStyle())
                            }
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
