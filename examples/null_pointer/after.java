// UserService.java - Fixed by Chronos
public class UserService {
    private PreferenceManager preferenceManager;
    private NotificationHandler notificationHandler;
    
    public UserService(PreferenceManager pm, NotificationHandler nh) {
        this.preferenceManager = pm;
        this.notificationHandler = nh;
    }
    
    public void updateUserSettings(Long userId, Map<String, Object> newSettings) {
        User user = userRepository.findById(userId);
        
        // Fixed: Retrieve or create default preferences
        UserPreferences prefs = preferenceManager.getPreferences(userId);
        if (prefs == null) {
            // Create default preferences for new users
            prefs = UserPreferences.createDefault(userId);
            preferenceManager.save(prefs);
        }
        
        // Now safe to access theme
        String theme = prefs.getTheme();
        
        if (newSettings.containsKey("theme")) {
            prefs.setTheme((String) newSettings.get("theme"));
        }
        
        // Safe access to email notifications
        boolean emailEnabled = prefs.isEmailNotificationsEnabled();
        
        if (emailEnabled && user != null && user.getEmail() != null) {
            notificationHandler.sendSettingsUpdateEmail(user, prefs);
        }
        
        preferenceManager.save(prefs);
        
        // Safe JSON conversion with null check
        logUserActivity(userId, "settings_update", prefs.toJson());
    }
    
    private void logUserActivity(Long userId, String action, String details) {
        if (details != null) {
            activityLogger.log(userId, action, details);
        }
    }
}

// PreferenceManager.java - Enhanced with Optional
public class PreferenceManager {
    private PreferenceRepository repository;
    
    public UserPreferences getPreferences(Long userId) {
        // Still returns null for backward compatibility
        return repository.findByUserId(userId);
    }
    
    // New method using Optional for modern code
    public Optional<UserPreferences> findPreferences(Long userId) {
        return Optional.ofNullable(repository.findByUserId(userId));
    }
    
    public void save(UserPreferences prefs) {
        Objects.requireNonNull(prefs, "Preferences cannot be null");
        repository.save(prefs);
    }
}

// NotificationHandler.java - Added validation
public class NotificationHandler {
    public void sendSettingsUpdateEmail(User user, UserPreferences prefs) {
        // Added null checks
        if (user == null || prefs == null) {
            logger.warn("Cannot send email: user or preferences is null");
            return;
        }
        
        String email = user.getEmail();
        if (email == null || email.isEmpty()) {
            logger.warn("Cannot send email: user has no email address");
            return;
        }
        
        String theme = prefs.getTheme();
        
        EmailTemplate template = templateEngine.load("settings_update");
        template.setVariable("theme", theme != null ? theme : "default");
        template.setVariable("user", user.getName() != null ? user.getName() : "User");
        
        emailService.send(email, template);
    }
}

// UserPreferences.java - Added factory method
public class UserPreferences {
    private Long userId;
    private String theme;
    private boolean emailNotificationsEnabled;
    
    // Factory method for default preferences
    public static UserPreferences createDefault(Long userId) {
        UserPreferences prefs = new UserPreferences();
        prefs.userId = userId;
        prefs.theme = "light"; // Default theme
        prefs.emailNotificationsEnabled = true; // Default to enabled
        return prefs;
    }
    
    // Getters and setters with null safety
    public String getTheme() {
        return theme != null ? theme : "light";
    }
    
    public String toJson() {
        // Safe JSON serialization
        try {
            return new ObjectMapper().writeValueAsString(this);
        } catch (JsonProcessingException e) {
            return "{}";
        }
    }
}