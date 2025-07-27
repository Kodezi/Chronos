// UserService.java - Contains the bug
public class UserService {
    private PreferenceManager preferenceManager;
    private NotificationHandler notificationHandler;
    
    public UserService(PreferenceManager pm, NotificationHandler nh) {
        this.preferenceManager = pm;
        this.notificationHandler = nh;
    }
    
    public void updateUserSettings(Long userId, Map<String, Object> newSettings) {
        User user = userRepository.findById(userId);
        
        // Bug: No null check after refactoring
        UserPreferences prefs = preferenceManager.getPreferences(userId);
        
        // This line throws NullPointerException when prefs is null
        String theme = prefs.getTheme();
        
        if (newSettings.containsKey("theme")) {
            prefs.setTheme((String) newSettings.get("theme"));
        }
        
        // Another potential NPE
        boolean emailEnabled = prefs.isEmailNotificationsEnabled();
        
        if (emailEnabled) {
            notificationHandler.sendSettingsUpdateEmail(user, prefs);
        }
        
        preferenceManager.save(prefs);
        
        // More operations that assume prefs is not null
        logUserActivity(userId, "settings_update", prefs.toJson());
    }
    
    private void logUserActivity(Long userId, String action, String details) {
        // Logging implementation
        activityLogger.log(userId, action, details);
    }
}

// PreferenceManager.java
public class PreferenceManager {
    private PreferenceRepository repository;
    
    public UserPreferences getPreferences(Long userId) {
        // Returns null for new users or users who haven't set preferences
        return repository.findByUserId(userId);
    }
    
    public void save(UserPreferences prefs) {
        repository.save(prefs);
    }
}

// NotificationHandler.java  
public class NotificationHandler {
    public void sendSettingsUpdateEmail(User user, UserPreferences prefs) {
        String email = user.getEmail();
        String theme = prefs.getTheme(); // Assumes prefs is not null
        
        EmailTemplate template = templateEngine.load("settings_update");
        template.setVariable("theme", theme);
        template.setVariable("user", user.getName());
        
        emailService.send(email, template);
    }
}