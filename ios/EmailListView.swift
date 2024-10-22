import SwiftUI

struct EmailListView: View {
    @StateObject var emailFetcher = EmailFetcher()  // Initialize EmailFetcher
    
    var body: some View {
        NavigationView {
            List(emailFetcher.emails) { email in
                VStack(alignment: .leading) {
                    Text(email.Subject).font(.headline)
                    Text(email.From).font(.subheadline).foregroundColor(.gray)
                }
                .padding(.vertical, 8)  // Add padding here to prevent content overlap
                .frame(maxWidth: .infinity, alignment: .leading)  // Set max width and alignment
            }
            .navigationTitle("Inbox")
            .onAppear {
                emailFetcher.fetchEmails()  // Fetch emails when the view appears
            }
        }
    }
}

