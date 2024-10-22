import Foundation
import SwiftUI

class EmailFetcher: ObservableObject {
    @Published var emails: [Email] = []

    func fetchEmails() {
        guard let url = URL(string: "http://127.0.0.1:8000/") else {
            print("Invalid URL")
            return
        }

        let task = URLSession.shared.dataTask(with: url) { data, response, error in
            if let data = data {
                do {
                    let decodedEmails = try JSONDecoder().decode([Email].self, from: data)
                    DispatchQueue.main.async {
                        self.emails = decodedEmails
                    }
                } catch {
                    print("Error decoding emails: \(error)")
                }
            } else if let error = error {
                print("Error fetching emails: \(error)")
            }
        }
        task.resume()
    }
}
