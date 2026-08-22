import SwiftUI
import UniformTypeIdentifiers
import PhotosUI

struct AddCourseView: View {
    @EnvironmentObject var viewModel: AppViewModel
    
    @State private var courseTitle = ""
    @State private var courseDescription = ""
    @State private var selectedCategory = "Программирование"
    let categories = ["Программирование", "Дизайн", "Математика", "Языки"]
    
    @State private var telegramLink = ""
    @State private var showSuccessAlert = false
    
    @State private var attachedFileName: String? = nil
    @State private var showDocumentPicker = false
    
    // ПЕРЕМЕННЫЕ ДЛЯ ФОТО ИЗ ГАЛЕРЕИ
    @State private var coverItem: PhotosPickerItem? = nil
    @State private var coverImageData: Data? = nil
    
    // ПЕРЕМЕННЫЕ ДЛЯ ВИДЕО ИЗ ГАЛЕРЕИ
    @State private var videoItem: PhotosPickerItem? = nil
    @State private var isProcessingVideo = false
    
    var body: some View {
        NavigationView {
            ScrollView(showsIndicators: false) {
                VStack(alignment: .leading, spacing: 24) {
                    
                    Text("Создать новый курс").font(.title2).fontWeight(.bold).padding(.horizontal).padding(.top, 20)
                    
                    VStack(alignment: .leading, spacing: 8) {
                        Text("НАЗВАНИЕ КУРСА").font(.caption).fontWeight(.bold).foregroundColor(.secondary)
                        TextField("Например: Высшая математика", text: $courseTitle)
                            .padding().background(Color(UIColor.secondarySystemBackground)).cornerRadius(16)
                    }
                    .padding(.horizontal)
                    
                    VStack(alignment: .leading, spacing: 8) {
                        Text("КАТЕГОРИЯ").font(.caption).fontWeight(.bold).foregroundColor(.secondary).padding(.horizontal)
                        ScrollView(.horizontal, showsIndicators: false) {
                            HStack(spacing: 12) {
                                ForEach(categories, id: \.self) { category in
                                    Text(category).font(.subheadline).fontWeight(.semibold)
                                        .padding(.horizontal, 16).padding(.vertical, 10)
                                        .background(selectedCategory == category ? Color.blue : Color(UIColor.secondarySystemBackground))
                                        .foregroundColor(selectedCategory == category ? .white : .primary)
                                        .cornerRadius(20)
                                        .onTapGesture { withAnimation(.spring()) { selectedCategory = category } }
                                }
                            }
                            .padding(.horizontal)
                        }
                    }
                    
                    VStack(alignment: .leading, spacing: 8) {
                        Text("ОПИСАНИЕ").font(.caption).fontWeight(.bold).foregroundColor(.secondary)
                        TextEditor(text: $courseDescription).frame(height: 100).padding(8).background(Color(UIColor.secondarySystemBackground)).cornerRadius(16)
                    }
                    .padding(.horizontal)
                    
                    VStack(alignment: .leading, spacing: 8) {
                        Text("ССЫЛКА НА TELEGRAM").font(.caption).fontWeight(.bold).foregroundColor(.secondary)
                        TextField("https://t.me/username", text: $telegramLink)
                            .padding().background(Color(UIColor.secondarySystemBackground)).cornerRadius(16).autocapitalization(.none)
                    }
                    .padding(.horizontal)
                    
                    // БЛОК: ВЫБОР ФОТО ОБЛОЖКИ ИЗ ГАЛЕРЕИ
                    VStack(alignment: .leading, spacing: 8) {
                        Text("ОБЛОЖКА КУРСА").font(.caption).fontWeight(.bold).foregroundColor(.secondary)
                        
                        PhotosPicker(selection: $coverItem, matching: .images) {
                            ZStack {
                                if let data = coverImageData, let uiImage = UIImage(data: data) {
                                    Image(uiImage: uiImage).resizable().scaledToFill().frame(height: 120).frame(maxWidth: .infinity).cornerRadius(16).clipped()
                                } else {
                                    RoundedRectangle(cornerRadius: 16).strokeBorder(style: StrokeStyle(lineWidth: 2, dash: [10])).foregroundColor(Color.blue.opacity(0.5)).frame(height: 120).background(Color.blue.opacity(0.05).cornerRadius(16))
                                    VStack(spacing: 8) {
                                        Image(systemName: "photo.on.rectangle.angled").font(.title)
                                        Text("Выбрать из Галереи").font(.subheadline)
                                    }.foregroundColor(.blue)
                                }
                            }
                        }
                        .onChange(of: coverItem) { _ in
                            Task {
                                if let data = try? await coverItem?.loadTransferable(type: Data.self) {
                                    coverImageData = data
                                }
                            }
                        }
                    }
                    .padding(.horizontal)
                    
                    // ОБНОВЛЕННЫЙ БЛОК МАТЕРИАЛОВ (РАЗДЕЛЕН НА PDF И ГАЛЕРЕЮ ВИДЕО)
                    VStack(alignment: .leading, spacing: 8) {
                        Text("МАТЕРИАЛЫ КУРСА").font(.caption).fontWeight(.bold).foregroundColor(.secondary)
                        
                        if attachedFileName == nil {
                            HStack(spacing: 12) {
                                // Кнопка 1: PDF из Файлов
                                Button(action: { showDocumentPicker = true }) {
                                    HStack {
                                        Image(systemName: "doc.fill")
                                        Text("PDF (Файлы)")
                                    }
                                    .font(.subheadline).fontWeight(.bold).foregroundColor(.white)
                                    .frame(maxWidth: .infinity).padding(.vertical, 12)
                                    .background(Color.blue).cornerRadius(12)
                                }
                                
                                // Кнопка 2: Видео из Галереи
                                PhotosPicker(selection: $videoItem, matching: .videos) {
                                    HStack {
                                        if isProcessingVideo {
                                            ProgressView().progressViewStyle(CircularProgressViewStyle(tint: .white))
                                            Text("Загрузка...")
                                        } else {
                                            Image(systemName: "play.rectangle.fill")
                                            Text("Видео (Галерея)")
                                        }
                                    }
                                    .font(.subheadline).fontWeight(.bold).foregroundColor(.white)
                                    .frame(maxWidth: .infinity).padding(.vertical, 12)
                                    .background(Color.purple).cornerRadius(12)
                                }
                                .disabled(isProcessingVideo) // Блокируем кнопку, пока грузится видео
                            }
                        } else {
                            // Показываем успешно прикрепленный файл
                            HStack(spacing: 16) {
                                ZStack {
                                    Circle().fill(Color.green.opacity(0.15)).frame(width: 44, height: 44)
                                    Image(systemName: attachedFileName!.lowercased().contains(".mp4") ? "play.rectangle.fill" : "doc.fill").foregroundColor(.green).font(.title3)
                                }
                                VStack(alignment: .leading, spacing: 4) {
                                    Text(attachedFileName!).font(.headline).foregroundColor(.primary).lineLimit(1).truncationMode(.middle)
                                    Text("Файл успешно добавлен").font(.caption).foregroundColor(.secondary)
                                }
                                Spacer()
                                Button(action: { attachedFileName = nil }) { Image(systemName: "trash.circle.fill").foregroundColor(.red).font(.title2) }
                            }
                            .padding().background(Color(UIColor.secondarySystemBackground)).cornerRadius(16)
                            .overlay(RoundedRectangle(cornerRadius: 16).stroke(Color.green.opacity(0.5), lineWidth: 1))
                        }
                    }
                    .padding(.horizontal)
                    
                    Button(action: {
                        guard !courseTitle.isEmpty, !courseDescription.isEmpty else { return }
                        
                        viewModel.addCourse(
                            title: courseTitle,
                            description: courseDescription,
                            category: selectedCategory,
                            telegramLink: telegramLink,
                            fileName: attachedFileName,
                            coverImageData: coverImageData
                        )
                        
                        courseTitle = ""; courseDescription = ""; telegramLink = ""; attachedFileName = nil; coverItem = nil; coverImageData = nil; videoItem = nil
                        showSuccessAlert = true
                        
                    }) {
                        Text("Опубликовать курс").font(.headline).foregroundColor(.white).frame(maxWidth: .infinity).padding().background(courseTitle.isEmpty ? Color.gray : Color.blue).cornerRadius(16)
                    }
                    .disabled(courseTitle.isEmpty || courseDescription.isEmpty).padding(.horizontal).padding(.top, 10)
                    
                }
                .padding(.bottom, 20)
            }
            .navigationBarHidden(true)
            .background(Color(UIColor.systemBackground))
            .alert(isPresented: $showSuccessAlert) { Alert(title: Text("Успех!"), message: Text("Курс успешно опубликован."), dismissButton: .default(Text("Отлично"))) }
            
            // Загрузка PDF из файлов
            .fileImporter(isPresented: $showDocumentPicker, allowedContentTypes: [.pdf], allowsMultipleSelection: false) { result in
                do {
                    let selectedFiles = try result.get()
                    if let firstFile = selectedFiles.first {
                        guard firstFile.startAccessingSecurityScopedResource() else { return }
                        defer { firstFile.stopAccessingSecurityScopedResource() }
                        let destUrl = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask).first!.appendingPathComponent(firstFile.lastPathComponent)
                        if FileManager.default.fileExists(atPath: destUrl.path) { try? FileManager.default.removeItem(at: destUrl) }
                        try FileManager.default.copyItem(at: firstFile, to: destUrl)
                        attachedFileName = firstFile.lastPathComponent
                    }
                } catch { print("Ошибка: \(error)") }
            }
            
            // Загрузка Видео из Галереи
            .onChange(of: videoItem) { _ in
                guard let item = videoItem else { return }
                isProcessingVideo = true // Показываем индикатор загрузки
                
                Task {
                    // Скачиваем видео напрямую из галереи в память приложения
                    if let data = try? await item.loadTransferable(type: Data.self) {
                        let fileName = "video_\(UUID().uuidString.prefix(6)).mp4"
                        if let url = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask).first?.appendingPathComponent(fileName) {
                            try? data.write(to: url)
                            
                            // Возвращаемся в главный поток для обновления UI
                            DispatchQueue.main.async {
                                attachedFileName = fileName
                                isProcessingVideo = false
                            }
                        }
                    } else {
                        DispatchQueue.main.async { isProcessingVideo = false }
                    }
                }
            }
        }
    }
}

#Preview {
    Group {
        AddCourseView().preferredColorScheme(.light).environmentObject(AppViewModel())
    }
}
