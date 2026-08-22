import SwiftUI
import AVKit

struct CourseDetailView: View {
    @Environment(\.dismiss) var dismiss
    @EnvironmentObject var viewModel: AppViewModel
    
    var course: LocalCourse
    
    // Динамически получаем курс из базы данных, чтобы звезды обновлялись моментально
    var currentCourse: LocalCourse {
        viewModel.courses.first(where: { $0.id == course.id }) ?? course
    }
    
    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 0) {
                
                ZStack(alignment: .topLeading) {
                    if let data = currentCourse.coverImageData, let uiImage = UIImage(data: data) {
                        Image(uiImage: uiImage).resizable().scaledToFill().frame(height: 280).clipped()
                        LinearGradient(gradient: Gradient(colors: [Color.black.opacity(0.6), Color.clear]), startPoint: .top, endPoint: .bottom).frame(height: 100)
                    } else {
                        LinearGradient(gradient: Gradient(colors: [Color.blue.opacity(0.8), Color.blue]), startPoint: .topLeading, endPoint: .bottomTrailing).frame(height: 280)
                        Image(systemName: "book.pages.fill").font(.system(size: 80)).foregroundColor(.white.opacity(0.3)).frame(maxWidth: .infinity, alignment: .center).padding(.top, 80)
                    }
                    
                    HStack {
                        Button(action: { dismiss() }) { Image(systemName: "chevron.left").font(.title3).fontWeight(.bold).foregroundColor(.white).padding(12).background(Color.black.opacity(0.4)).clipShape(Circle()) }
                        Spacer()
                        Button(action: { viewModel.toggleFavorite(id: currentCourse.id) }) { Image(systemName: currentCourse.isFavorite ? "heart.fill" : "heart").font(.title3).fontWeight(.bold).foregroundColor(currentCourse.isFavorite ? .red : .white).padding(12).background(Color.black.opacity(0.4)).clipShape(Circle()) }
                    }
                    .padding(.horizontal, 16).padding(.top, 50)
                }
                
                VStack(alignment: .leading, spacing: 24) {
                    
                    VStack(alignment: .leading, spacing: 8) {
                        HStack {
                            Text(currentCourse.category).font(.caption).fontWeight(.bold).padding(.horizontal, 12).padding(.vertical, 6).background(Color.blue.opacity(0.1)).foregroundColor(.blue).cornerRadius(8)
                            Spacer()
                            
                            // РАБОЧИЕ КЛИКАБЕЛЬНЫЕ ЗВЕЗДЫ!
                            HStack(spacing: 4) {
                                ForEach(1...5, id: \.self) { star in
                                    Image(systemName: star <= Int(currentCourse.rating) ? "star.fill" : "star")
                                        .foregroundColor(.yellow)
                                        .font(.title3)
                                        .onTapGesture {
                                            withAnimation {
                                                viewModel.rateCourse(id: currentCourse.id, newRating: Double(star))
                                            }
                                        }
                                }
                                Text(String(format: "%.1f", currentCourse.rating)).fontWeight(.bold).padding(.leading, 4)
                            }
                        }
                        Text(currentCourse.title).font(.title).fontWeight(.heavy)
                        Text("Автор: \(currentCourse.authorName)").font(.subheadline).foregroundColor(.secondary)
                    }
                    
                    VStack(alignment: .leading, spacing: 8) {
                        Text("О курсе").font(.title3).fontWeight(.bold)
                        Text(currentCourse.description).foregroundColor(.secondary).lineSpacing(4)
                    }
                    
                    if let fileName = currentCourse.attachedFileName {
                        VStack(alignment: .leading, spacing: 12) {
                            Text("Материалы").font(.title3).fontWeight(.bold)
                            let isVideo = fileName.lowercased().contains(".mp4") || fileName.lowercased().contains(".mov")
                            if isVideo {
                                let docURL = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask).first!.appendingPathComponent(fileName)
                                if FileManager.default.fileExists(atPath: docURL.path) {
                                    VideoPlayer(player: AVPlayer(url: docURL)).frame(height: 220).cornerRadius(16).shadow(color: Color.black.opacity(0.1), radius: 8, x: 0, y: 4)
                                } else {
                                    Text("⚠️ Видеофайл не найден в памяти устройства.").font(.caption).foregroundColor(.red).padding().background(Color.red.opacity(0.1)).cornerRadius(12)
                                }
                            } else {
                                HStack(spacing: 16) {
                                    Image(systemName: "doc.fill").foregroundColor(.red).font(.title2)
                                    Text(fileName).fontWeight(.semibold).lineLimit(1).truncationMode(.middle)
                                    Spacer()
                                    Image(systemName: "arrow.down.circle").foregroundColor(.blue).font(.title2)
                                }
                                .padding().background(Color(UIColor.secondarySystemBackground)).cornerRadius(12)
                            }
                        }
                    }
                    
                    Button(action: {
                        if let url = URL(string: currentCourse.telegramLink) { UIApplication.shared.open(url) }
                    }) {
                        HStack {
                            Image(systemName: "paperplane.fill")
                            Text("Связаться с автором").fontWeight(.bold)
                        }
                        .foregroundColor(.white).frame(maxWidth: .infinity).padding().background(Color(red: 0.17, green: 0.65, blue: 0.86)).cornerRadius(16)
                    }
                    .padding(.top, 10)
                    
                    Button(action: {
                        viewModel.deleteCourse(id: currentCourse.id)
                        dismiss()
                    }) {
                        HStack {
                            Image(systemName: "trash")
                            Text("Удалить курс")
                        }
                        .foregroundColor(.red).frame(maxWidth: .infinity).padding().background(Color.red.opacity(0.1)).cornerRadius(16)
                    }
                }
                .padding(20).background(Color(UIColor.systemBackground)).cornerRadius(24, corners: [.topLeft, .topRight]).offset(y: -30)
            }
        }
        .edgesIgnoringSafeArea(.top)
        .navigationBarHidden(true)
    }
}

extension View {
    func cornerRadius(_ radius: CGFloat, corners: UIRectCorner) -> some View { clipShape(RoundedCorner(radius: radius, corners: corners)) }
}
struct RoundedCorner: Shape {
    var radius: CGFloat = .infinity; var corners: UIRectCorner = .allCorners
    func path(in rect: CGRect) -> Path { return Path(UIBezierPath(roundedRect: rect, byRoundingCorners: corners, cornerRadii: CGSize(width: radius, height: radius)).cgPath) }
}
