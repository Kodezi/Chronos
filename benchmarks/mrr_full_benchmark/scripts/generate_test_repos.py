#!/usr/bin/env python3
"""
Generate test repository structures for MRR benchmark evaluation.
Creates realistic codebases with bugs injected at specific commits.
"""

import os
import json
import random
import shutil
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Tuple


class TestRepoGenerator:
    """Generate test repositories with realistic code and bug injections"""
    
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.repos_path = self.base_path / "test_repositories"
        self.repos_path.mkdir(exist_ok=True)
        
    def generate_all_repos(self):
        """Generate all test repositories according to distribution"""
        print("Generating test repositories...")
        
        # Repository distributions from metadata
        repo_configs = [
            ("small", 10, "<10K LOC", 50),
            ("medium", 30, "10K-100K LOC", 100),
            ("large", 20, "100K-1M LOC", 150),
            ("enterprise", 5, ">1M LOC", 200)
        ]
        
        total_repos = 0
        for size_category, count, size_desc, bugs_per_repo in repo_configs:
            print(f"\nGenerating {count} {size_category} repositories ({size_desc})...")
            
            for i in range(count):
                repo_name = f"{size_category}_repo_{i+1:02d}"
                self._generate_repository(repo_name, size_category, bugs_per_repo)
                total_repos += 1
                print(f"  Created {repo_name}")
        
        print(f"\n✓ Generated {total_repos} test repositories!")
        self._create_repos_metadata()
    
    def _generate_repository(self, repo_name: str, size_category: str, num_bugs: int):
        """Generate a single repository with injected bugs"""
        repo_path = self.repos_path / repo_name
        
        # Remove if exists
        if repo_path.exists():
            shutil.rmtree(repo_path)
        
        repo_path.mkdir()
        
        # Initialize git repo
        self._init_git_repo(repo_path)
        
        # Generate code structure based on size
        if size_category == "small":
            self._generate_small_repo(repo_path)
        elif size_category == "medium":
            self._generate_medium_repo(repo_path)
        elif size_category == "large":
            self._generate_large_repo(repo_path)
        else:  # enterprise
            self._generate_enterprise_repo(repo_path)
        
        # Create initial commit
        self._git_commit(repo_path, "Initial commit")
        
        # Generate development history with bug injections
        self._generate_development_history(repo_path, num_bugs)
        
        # Create repo metadata
        self._create_repo_metadata(repo_path, repo_name, size_category, num_bugs)
    
    def _init_git_repo(self, repo_path: Path):
        """Initialize a git repository"""
        subprocess.run(["git", "init"], cwd=repo_path, capture_output=True)
        subprocess.run(["git", "config", "user.name", "MRR Generator"], cwd=repo_path, capture_output=True)
        subprocess.run(["git", "config", "user.email", "mrr@kodezi.com"], cwd=repo_path, capture_output=True)
    
    def _git_commit(self, repo_path: Path, message: str):
        """Create a git commit"""
        subprocess.run(["git", "add", "-A"], cwd=repo_path, capture_output=True)
        subprocess.run(["git", "commit", "-m", message], cwd=repo_path, capture_output=True)
    
    def _generate_small_repo(self, repo_path: Path):
        """Generate a small repository structure (<10K LOC)"""
        # Simple web app structure
        dirs = [
            "src",
            "src/controllers",
            "src/models",
            "src/utils",
            "tests",
            "config"
        ]
        
        for dir_path in dirs:
            (repo_path / dir_path).mkdir(parents=True, exist_ok=True)
        
        # Generate Python files
        self._create_file(repo_path / "src/app.py", self._generate_python_app_code())
        self._create_file(repo_path / "src/controllers/user.py", self._generate_python_controller())
        self._create_file(repo_path / "src/controllers/auth.py", self._generate_python_auth_controller())
        self._create_file(repo_path / "src/models/user.py", self._generate_python_model())
        self._create_file(repo_path / "src/utils/helpers.py", self._generate_python_utils())
        self._create_file(repo_path / "tests/test_user.py", self._generate_python_test())
        self._create_file(repo_path / "config/settings.py", self._generate_python_config())
        
        # Add requirements and README
        self._create_file(repo_path / "requirements.txt", self._generate_requirements())
        self._create_file(repo_path / "README.md", self._generate_readme("Small Web Application"))
        self._create_file(repo_path / ".gitignore", self._generate_gitignore())
    
    def _generate_medium_repo(self, repo_path: Path):
        """Generate a medium repository structure (10K-100K LOC)"""
        # More complex application with multiple components
        dirs = [
            "backend/src/main/java/com/example/api",
            "backend/src/main/java/com/example/service",
            "backend/src/main/java/com/example/repository",
            "backend/src/main/java/com/example/model",
            "backend/src/test/java/com/example",
            "frontend/src/components",
            "frontend/src/services",
            "frontend/src/utils",
            "frontend/tests",
            "docs",
            "scripts",
            "config"
        ]
        
        for dir_path in dirs:
            (repo_path / dir_path).mkdir(parents=True, exist_ok=True)
        
        # Generate Java backend files
        self._create_file(repo_path / "backend/src/main/java/com/example/Application.java", 
                         self._generate_java_application())
        self._create_file(repo_path / "backend/src/main/java/com/example/api/UserController.java", 
                         self._generate_java_controller())
        self._create_file(repo_path / "backend/src/main/java/com/example/service/UserService.java", 
                         self._generate_java_service())
        self._create_file(repo_path / "backend/src/main/java/com/example/repository/UserRepository.java", 
                         self._generate_java_repository())
        self._create_file(repo_path / "backend/src/main/java/com/example/model/User.java", 
                         self._generate_java_model())
        
        # Generate JavaScript frontend files
        self._create_file(repo_path / "frontend/src/App.js", self._generate_react_app())
        self._create_file(repo_path / "frontend/src/components/UserList.js", self._generate_react_component())
        self._create_file(repo_path / "frontend/src/services/api.js", self._generate_js_service())
        self._create_file(repo_path / "frontend/src/utils/helpers.js", self._generate_js_utils())
        
        # Configuration files
        self._create_file(repo_path / "backend/pom.xml", self._generate_pom_xml())
        self._create_file(repo_path / "frontend/package.json", self._generate_package_json())
        self._create_file(repo_path / "docker-compose.yml", self._generate_docker_compose())
        self._create_file(repo_path / "README.md", self._generate_readme("Full Stack Application"))
    
    def _generate_large_repo(self, repo_path: Path):
        """Generate a large repository structure (100K-1M LOC)"""
        # Microservices architecture
        services = ["auth", "user", "order", "payment", "notification", "analytics"]
        
        for service in services:
            service_dirs = [
                f"services/{service}/src/main/java/com/example/{service}/controller",
                f"services/{service}/src/main/java/com/example/{service}/service",
                f"services/{service}/src/main/java/com/example/{service}/repository",
                f"services/{service}/src/main/java/com/example/{service}/model",
                f"services/{service}/src/main/java/com/example/{service}/config",
                f"services/{service}/src/test/java/com/example/{service}",
                f"services/{service}/src/main/resources"
            ]
            
            for dir_path in service_dirs:
                (repo_path / dir_path).mkdir(parents=True, exist_ok=True)
            
            # Generate multiple files per service
            self._generate_service_files(repo_path, service)
        
        # Shared libraries
        lib_dirs = [
            "libs/common/src",
            "libs/security/src",
            "libs/messaging/src"
        ]
        
        for dir_path in lib_dirs:
            (repo_path / dir_path).mkdir(parents=True, exist_ok=True)
        
        # Infrastructure and deployment
        infra_dirs = [
            "infrastructure/kubernetes",
            "infrastructure/terraform",
            "infrastructure/monitoring"
        ]
        
        for dir_path in infra_dirs:
            (repo_path / dir_path).mkdir(parents=True, exist_ok=True)
        
        self._create_file(repo_path / "README.md", self._generate_readme("Microservices Platform"))
    
    def _generate_enterprise_repo(self, repo_path: Path):
        """Generate an enterprise repository structure (>1M LOC)"""
        # Large monolithic enterprise application
        modules = [
            "core", "web", "api", "batch", "integration", 
            "reporting", "admin", "mobile", "analytics", "ml"
        ]
        
        for module in modules:
            module_dirs = [
                f"modules/{module}/src/main/java",
                f"modules/{module}/src/main/resources",
                f"modules/{module}/src/test/java",
                f"modules/{module}/src/test/resources"
            ]
            
            for dir_path in module_dirs:
                (repo_path / dir_path).mkdir(parents=True, exist_ok=True)
            
            # Generate many files per module
            self._generate_enterprise_module_files(repo_path, module)
        
        # Legacy code sections
        legacy_dirs = [
            "legacy/cobol-bridge",
            "legacy/mainframe-connector",
            "legacy/batch-jobs"
        ]
        
        for dir_path in legacy_dirs:
            (repo_path / dir_path).mkdir(parents=True, exist_ok=True)
        
        self._create_file(repo_path / "README.md", self._generate_readme("Enterprise System"))
    
    def _generate_development_history(self, repo_path: Path, num_bugs: int):
        """Generate realistic development history with bug injections"""
        # Simulate 12 months of development
        current_date = datetime.now()
        start_date = current_date - timedelta(days=365)
        
        # Create commits over time
        num_commits = random.randint(500, 2000)
        bug_injection_points = sorted(random.sample(range(50, num_commits), min(num_bugs, num_commits - 50)))
        
        for i in range(num_commits):
            # Calculate commit date
            progress = i / num_commits
            commit_date = start_date + timedelta(days=int(365 * progress))
            
            # Make some changes
            self._make_random_changes(repo_path)
            
            # Check if this is a bug injection point
            if i in bug_injection_points:
                bug_index = bug_injection_points.index(i)
                self._inject_bug(repo_path, f"bug_{bug_index+1:03d}")
                commit_msg = f"Feature: Add new functionality (contains bug_{bug_index+1:03d})"
            else:
                commit_msg = self._generate_commit_message()
            
            # Set commit date and create commit
            env = os.environ.copy()
            env['GIT_AUTHOR_DATE'] = commit_date.isoformat()
            env['GIT_COMMITTER_DATE'] = commit_date.isoformat()
            
            subprocess.run(["git", "add", "-A"], cwd=repo_path, capture_output=True)
            subprocess.run(["git", "commit", "-m", commit_msg], cwd=repo_path, capture_output=True, env=env)
    
    def _make_random_changes(self, repo_path: Path):
        """Make random realistic changes to repository"""
        change_types = [
            self._add_new_method,
            self._modify_existing_method,
            self._add_new_file,
            self._update_config,
            self._add_test
        ]
        
        # Make 1-5 changes
        num_changes = random.randint(1, 5)
        for _ in range(num_changes):
            change_func = random.choice(change_types)
            change_func(repo_path)
    
    def _inject_bug(self, repo_path: Path, bug_id: str):
        """Inject a specific bug into the repository"""
        bug_types = [
            self._inject_null_pointer_bug,
            self._inject_off_by_one_bug,
            self._inject_race_condition_bug,
            self._inject_memory_leak_bug,
            self._inject_api_misuse_bug
        ]
        
        bug_func = random.choice(bug_types)
        bug_func(repo_path, bug_id)
    
    # Code generation helpers
    def _generate_python_app_code(self) -> str:
        return '''from flask import Flask, jsonify
from controllers.user import user_blueprint
from controllers.auth import auth_blueprint
import config.settings as settings

app = Flask(__name__)
app.config.from_object(settings)

# Register blueprints
app.register_blueprint(user_blueprint, url_prefix='/api/users')
app.register_blueprint(auth_blueprint, url_prefix='/api/auth')

@app.route('/health')
def health_check():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    app.run(debug=settings.DEBUG, port=settings.PORT)
'''

    def _generate_python_controller(self) -> str:
        return '''from flask import Blueprint, request, jsonify
from models.user import User
from utils.helpers import validate_email

user_blueprint = Blueprint('user', __name__)

@user_blueprint.route('/', methods=['GET'])
def get_users():
    """Get all users"""
    users = User.get_all()
    return jsonify([user.to_dict() for user in users])

@user_blueprint.route('/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Get user by ID"""
    user = User.get_by_id(user_id)
    if user:
        return jsonify(user.to_dict())
    return jsonify({'error': 'User not found'}), 404

@user_blueprint.route('/', methods=['POST'])
def create_user():
    """Create new user"""
    data = request.get_json()
    
    if not validate_email(data.get('email')):
        return jsonify({'error': 'Invalid email'}), 400
    
    user = User.create(data)
    return jsonify(user.to_dict()), 201
'''

    def _generate_python_auth_controller(self) -> str:
        return '''from flask import Blueprint, request, jsonify
import jwt
from datetime import datetime, timedelta
from models.user import User
import config.settings as settings

auth_blueprint = Blueprint('auth', __name__)

@auth_blueprint.route('/login', methods=['POST'])
def login():
    """User login"""
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    user = User.authenticate(email, password)
    if not user:
        return jsonify({'error': 'Invalid credentials'}), 401
    
    # Generate JWT token
    payload = {
        'user_id': user.id,
        'exp': datetime.utcnow() + timedelta(hours=24)
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
    
    return jsonify({'token': token})

@auth_blueprint.route('/logout', methods=['POST'])
def logout():
    """User logout"""
    # In a real app, you might invalidate the token here
    return jsonify({'message': 'Logged out successfully'})
'''

    def _generate_python_model(self) -> str:
        return '''from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User:
    """User model"""
    
    users = []  # In-memory storage for demo
    next_id = 1
    
    def __init__(self, id, email, password_hash, created_at):
        self.id = id
        self.email = email
        self.password_hash = password_hash
        self.created_at = created_at
    
    @classmethod
    def create(cls, data):
        """Create new user"""
        user = cls(
            id=cls.next_id,
            email=data['email'],
            password_hash=generate_password_hash(data['password']),
            created_at=datetime.utcnow()
        )
        cls.users.append(user)
        cls.next_id += 1
        return user
    
    @classmethod
    def get_all(cls):
        """Get all users"""
        return cls.users
    
    @classmethod
    def get_by_id(cls, user_id):
        """Get user by ID"""
        for user in cls.users:
            if user.id == user_id:
                return user
        return None
    
    @classmethod
    def authenticate(cls, email, password):
        """Authenticate user"""
        for user in cls.users:
            if user.email == email and check_password_hash(user.password_hash, password):
                return user
        return None
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'email': self.email,
            'created_at': self.created_at.isoformat()
        }
'''

    def _generate_python_utils(self) -> str:
        return '''import re
from functools import wraps
from flask import request, jsonify
import jwt
import config.settings as settings

def validate_email(email):
    """Validate email format"""
    if not email:
        return False
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None

def require_auth(f):
    """Authentication decorator"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'No token provided'}), 401
        
        try:
            token = token.split(' ')[1]  # Remove 'Bearer ' prefix
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            request.user_id = payload['user_id']
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        
        return f(*args, **kwargs)
    
    return decorated_function

def paginate(query, page=1, per_page=20):
    """Paginate query results"""
    total = len(query)
    start = (page - 1) * per_page
    end = start + per_page
    
    items = query[start:end]
    
    return {
        'items': items,
        'total': total,
        'page': page,
        'per_page': per_page,
        'pages': (total + per_page - 1) // per_page
    }
'''

    def _generate_python_test(self) -> str:
        return '''import unittest
from app import app
from models.user import User

class TestUserAPI(unittest.TestCase):
    """Test user API endpoints"""
    
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        User.users = []  # Clear users
        User.next_id = 1
    
    def test_create_user(self):
        """Test user creation"""
        response = self.app.post('/api/users/', 
            json={'email': 'test@example.com', 'password': 'secret123'})
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertEqual(data['email'], 'test@example.com')
    
    def test_get_user(self):
        """Test getting user by ID"""
        # Create user first
        user = User.create({'email': 'test@example.com', 'password': 'secret123'})
        
        response = self.app.get(f'/api/users/{user.id}')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['email'], 'test@example.com')
    
    def test_invalid_email(self):
        """Test invalid email validation"""
        response = self.app.post('/api/users/', 
            json={'email': 'invalid-email', 'password': 'secret123'})
        self.assertEqual(response.status_code, 400)

if __name__ == '__main__':
    unittest.main()
'''

    def _generate_python_config(self) -> str:
        return '''import os
from datetime import timedelta

# Flask settings
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
PORT = int(os.environ.get('PORT', 5000))
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Database settings (for demo using in-memory)
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///app.db')

# JWT settings
JWT_EXPIRATION = timedelta(hours=24)
JWT_ALGORITHM = 'HS256'

# Pagination
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

# Email settings
SMTP_HOST = os.environ.get('SMTP_HOST', 'localhost')
SMTP_PORT = int(os.environ.get('SMTP_PORT', 587))

# Cache settings
CACHE_TYPE = 'simple'
CACHE_DEFAULT_TIMEOUT = 300

# Security
CSRF_ENABLED = True
SESSION_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_HTTPONLY = True
'''

    def _generate_java_application(self) -> str:
        return '''package com.example;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.Bean;
import org.springframework.web.servlet.config.annotation.CorsRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

@SpringBootApplication
public class Application {
    
    public static void main(String[] args) {
        SpringApplication.run(Application.class, args);
    }
    
    @Bean
    public WebMvcConfigurer corsConfigurer() {
        return new WebMvcConfigurer() {
            @Override
            public void addCorsMappings(CorsRegistry registry) {
                registry.addMapping("/api/**")
                    .allowedOrigins("http://localhost:3000")
                    .allowedMethods("GET", "POST", "PUT", "DELETE")
                    .allowedHeaders("*")
                    .allowCredentials(true);
            }
        };
    }
}
'''

    def _generate_java_controller(self) -> str:
        return '''package com.example.api;

import com.example.model.User;
import com.example.service.UserService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import javax.validation.Valid;
import java.util.List;

@RestController
@RequestMapping("/api/users")
public class UserController {
    
    @Autowired
    private UserService userService;
    
    @GetMapping
    public ResponseEntity<List<User>> getAllUsers() {
        List<User> users = userService.getAllUsers();
        return ResponseEntity.ok(users);
    }
    
    @GetMapping("/{id}")
    public ResponseEntity<User> getUserById(@PathVariable Long id) {
        User user = userService.getUserById(id);
        if (user != null) {
            return ResponseEntity.ok(user);
        }
        return ResponseEntity.notFound().build();
    }
    
    @PostMapping
    public ResponseEntity<User> createUser(@Valid @RequestBody User user) {
        User createdUser = userService.createUser(user);
        return ResponseEntity.status(HttpStatus.CREATED).body(createdUser);
    }
    
    @PutMapping("/{id}")
    public ResponseEntity<User> updateUser(@PathVariable Long id, @Valid @RequestBody User user) {
        User updatedUser = userService.updateUser(id, user);
        if (updatedUser != null) {
            return ResponseEntity.ok(updatedUser);
        }
        return ResponseEntity.notFound().build();
    }
    
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteUser(@PathVariable Long id) {
        boolean deleted = userService.deleteUser(id);
        if (deleted) {
            return ResponseEntity.noContent().build();
        }
        return ResponseEntity.notFound().build();
    }
}
'''

    def _generate_java_service(self) -> str:
        return '''package com.example.service;

import com.example.model.User;
import com.example.repository.UserRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.Optional;

@Service
@Transactional
public class UserService {
    
    @Autowired
    private UserRepository userRepository;
    
    public List<User> getAllUsers() {
        return userRepository.findAll();
    }
    
    public User getUserById(Long id) {
        Optional<User> user = userRepository.findById(id);
        return user.orElse(null);
    }
    
    public User createUser(User user) {
        // Add business logic here
        user.setCreatedAt(new java.util.Date());
        return userRepository.save(user);
    }
    
    public User updateUser(Long id, User userDetails) {
        Optional<User> optionalUser = userRepository.findById(id);
        if (optionalUser.isPresent()) {
            User user = optionalUser.get();
            user.setEmail(userDetails.getEmail());
            user.setName(userDetails.getName());
            user.setUpdatedAt(new java.util.Date());
            return userRepository.save(user);
        }
        return null;
    }
    
    public boolean deleteUser(Long id) {
        if (userRepository.existsById(id)) {
            userRepository.deleteById(id);
            return true;
        }
        return false;
    }
}
'''

    def _generate_java_repository(self) -> str:
        return '''package com.example.repository;

import com.example.model.User;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface UserRepository extends JpaRepository<User, Long> {
    
    Optional<User> findByEmail(String email);
    
    List<User> findByNameContaining(String name);
    
    @Query("SELECT u FROM User u WHERE u.active = true")
    List<User> findAllActiveUsers();
    
    boolean existsByEmail(String email);
}
'''

    def _generate_java_model(self) -> str:
        return '''package com.example.model;

import javax.persistence.*;
import javax.validation.constraints.Email;
import javax.validation.constraints.NotBlank;
import java.util.Date;

@Entity
@Table(name = "users")
public class User {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @NotBlank
    @Column(nullable = false)
    private String name;
    
    @Email
    @NotBlank
    @Column(nullable = false, unique = true)
    private String email;
    
    @Column(nullable = false)
    private String password;
    
    @Column(name = "active")
    private boolean active = true;
    
    @Temporal(TemporalType.TIMESTAMP)
    @Column(name = "created_at", nullable = false)
    private Date createdAt;
    
    @Temporal(TemporalType.TIMESTAMP)
    @Column(name = "updated_at")
    private Date updatedAt;
    
    // Constructors
    public User() {}
    
    public User(String name, String email, String password) {
        this.name = name;
        this.email = email;
        this.password = password;
        this.createdAt = new Date();
    }
    
    // Getters and setters
    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    
    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
    
    public String getEmail() { return email; }
    public void setEmail(String email) { this.email = email; }
    
    public String getPassword() { return password; }
    public void setPassword(String password) { this.password = password; }
    
    public boolean isActive() { return active; }
    public void setActive(boolean active) { this.active = active; }
    
    public Date getCreatedAt() { return createdAt; }
    public void setCreatedAt(Date createdAt) { this.createdAt = createdAt; }
    
    public Date getUpdatedAt() { return updatedAt; }
    public void setUpdatedAt(Date updatedAt) { this.updatedAt = updatedAt; }
}
'''

    def _generate_react_app(self) -> str:
        return '''import React, { useState, useEffect } from 'react';
import UserList from './components/UserList';
import api from './services/api';
import './App.css';

function App() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      setLoading(true);
      const data = await api.getUsers();
      setUsers(data);
      setError(null);
    } catch (err) {
      setError('Failed to fetch users');
      console.error('Error fetching users:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="loading">Loading...</div>;
  if (error) return <div className="error">{error}</div>;

  return (
    <div className="App">
      <header className="App-header">
        <h1>User Management System</h1>
      </header>
      <main>
        <UserList users={users} onRefresh={fetchUsers} />
      </main>
    </div>
  );
}

export default App;
'''

    def _generate_react_component(self) -> str:
        return '''import React from 'react';
import PropTypes from 'prop-types';

const UserList = ({ users, onRefresh }) => {
  return (
    <div className="user-list">
      <div className="user-list-header">
        <h2>Users ({users.length})</h2>
        <button onClick={onRefresh}>Refresh</button>
      </div>
      
      {users.length === 0 ? (
        <p>No users found</p>
      ) : (
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Name</th>
              <th>Email</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {users.map(user => (
              <tr key={user.id}>
                <td>{user.id}</td>
                <td>{user.name}</td>
                <td>{user.email}</td>
                <td>{user.active ? 'Active' : 'Inactive'}</td>
                <td>
                  <button>Edit</button>
                  <button>Delete</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
};

UserList.propTypes = {
  users: PropTypes.arrayOf(PropTypes.shape({
    id: PropTypes.number.isRequired,
    name: PropTypes.string.isRequired,
    email: PropTypes.string.isRequired,
    active: PropTypes.bool
  })).isRequired,
  onRefresh: PropTypes.func.isRequired
};

export default UserList;
'''

    def _generate_js_service(self) -> str:
        return '''const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8080/api';

class ApiService {
  async request(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    const config = {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    };

    const response = await fetch(url, config);
    
    if (!response.ok) {
      throw new Error(`API Error: ${response.statusText}`);
    }
    
    return response.json();
  }

  async getUsers() {
    return this.request('/users');
  }

  async getUser(id) {
    return this.request(`/users/${id}`);
  }

  async createUser(userData) {
    return this.request('/users', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
  }

  async updateUser(id, userData) {
    return this.request(`/users/${id}`, {
      method: 'PUT',
      body: JSON.stringify(userData),
    });
  }

  async deleteUser(id) {
    return this.request(`/users/${id}`, {
      method: 'DELETE',
    });
  }
}

export default new ApiService();
'''

    def _generate_js_utils(self) -> str:
        return '''export const formatDate = (date) => {
  const options = { year: 'numeric', month: 'long', day: 'numeric' };
  return new Date(date).toLocaleDateString(undefined, options);
};

export const validateEmail = (email) => {
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return re.test(email);
};

export const debounce = (func, wait) => {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
};

export const generateId = () => {
  return '_' + Math.random().toString(36).substr(2, 9);
};

export const deepClone = (obj) => {
  return JSON.parse(JSON.stringify(obj));
};

export const sortByProperty = (array, property, ascending = true) => {
  return array.sort((a, b) => {
    if (ascending) {
      return a[property] > b[property] ? 1 : -1;
    }
    return a[property] < b[property] ? 1 : -1;
  });
};
'''

    def _generate_requirements(self) -> str:
        return '''Flask==2.3.2
Flask-CORS==4.0.0
PyJWT==2.8.0
Werkzeug==2.3.6
python-dotenv==1.0.0
gunicorn==21.2.0
pytest==7.4.0
pytest-cov==4.1.0
flake8==6.0.0
black==23.7.0
'''

    def _generate_package_json(self) -> str:
        return '''{
  "name": "frontend",
  "version": "1.0.0",
  "private": true,
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-scripts": "5.0.1",
    "prop-types": "^15.8.1"
  },
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test",
    "eject": "react-scripts eject"
  },
  "eslintConfig": {
    "extends": [
      "react-app",
      "react-app/jest"
    ]
  },
  "browserslist": {
    "production": [
      ">0.2%",
      "not dead",
      "not op_mini all"
    ],
    "development": [
      "last 1 chrome version",
      "last 1 firefox version",
      "last 1 safari version"
    ]
  }
}
'''

    def _generate_pom_xml(self) -> str:
        return '''<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 
         http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    
    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>2.7.14</version>
    </parent>
    
    <groupId>com.example</groupId>
    <artifactId>backend</artifactId>
    <version>1.0.0</version>
    <packaging>jar</packaging>
    
    <properties>
        <java.version>11</java.version>
    </properties>
    
    <dependencies>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-data-jpa</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-validation</artifactId>
        </dependency>
        <dependency>
            <groupId>com.h2database</groupId>
            <artifactId>h2</artifactId>
            <scope>runtime</scope>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-test</artifactId>
            <scope>test</scope>
        </dependency>
    </dependencies>
    
    <build>
        <plugins>
            <plugin>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-maven-plugin</artifactId>
            </plugin>
        </plugins>
    </build>
</project>
'''

    def _generate_docker_compose(self) -> str:
        return '''version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8080:8080"
    environment:
      - SPRING_PROFILES_ACTIVE=dev
      - DATABASE_URL=jdbc:postgresql://db:5432/appdb
      - DATABASE_USERNAME=appuser
      - DATABASE_PASSWORD=apppass
    depends_on:
      - db
    networks:
      - app-network

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_API_URL=http://localhost:8080/api
    depends_on:
      - backend
    networks:
      - app-network

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=appdb
      - POSTGRES_USER=appuser
      - POSTGRES_PASSWORD=apppass
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - app-network

volumes:
  postgres_data:

networks:
  app-network:
    driver: bridge
'''

    def _generate_readme(self, project_type: str) -> str:
        return f'''# {project_type}

This is a test repository for the Kodezi Chronos MRR benchmark.

## Overview

This repository contains intentionally injected bugs for debugging evaluation purposes.

## Structure

- Source code with realistic application structure
- Test suites with comprehensive coverage
- Configuration files
- Development history with bug injections

## Usage

This repository is part of the MRR benchmark and should be used with the Chronos evaluation framework.

## Bug Injections

Bugs have been injected at specific commits throughout the development history. Each bug is documented in the repository metadata.

## Warning

This is a synthetic repository created for benchmark purposes. Do not use in production.
'''

    def _generate_gitignore(self) -> str:
        return '''# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.venv
.env

# Java
target/
*.class
*.jar
*.war
*.ear
.settings/
.project
.classpath

# JavaScript/Node
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*
.npm
dist/
build/

# IDEs
.idea/
.vscode/
*.swp
*.swo
*~
.DS_Store

# Testing
.coverage
htmlcov/
.pytest_cache/
test-results/

# Logs
*.log
logs/

# Database
*.db
*.sqlite
'''

    # Helper methods for generating service files
    def _generate_service_files(self, repo_path: Path, service: str):
        """Generate files for a microservice"""
        base_package = f"com.example.{service}"
        
        # Controller
        controller_code = f'''package {base_package}.controller;

import org.springframework.web.bind.annotation.*;
import {base_package}.service.{service.capitalize()}Service;

@RestController
@RequestMapping("/api/{service}")
public class {service.capitalize()}Controller {{
    // Controller implementation
}}
'''
        self._create_file(
            repo_path / f"services/{service}/src/main/java/com/example/{service}/controller/{service.capitalize()}Controller.java",
            controller_code
        )
        
        # Service
        service_code = f'''package {base_package}.service;

import org.springframework.stereotype.Service;

@Service
public class {service.capitalize()}Service {{
    // Service implementation
}}
'''
        self._create_file(
            repo_path / f"services/{service}/src/main/java/com/example/{service}/service/{service.capitalize()}Service.java",
            service_code
        )

    def _generate_enterprise_module_files(self, repo_path: Path, module: str):
        """Generate files for an enterprise module"""
        # Generate multiple packages and classes per module
        packages = ["controller", "service", "repository", "model", "dto", "mapper", "validator", "exception"]
        
        for package in packages:
            for i in range(random.randint(5, 15)):  # Multiple classes per package
                class_name = f"{module.capitalize()}{package.capitalize()}{i+1}"
                file_path = repo_path / f"modules/{module}/src/main/java/com/enterprise/{module}/{package}/{class_name}.java"
                
                code = f'''package com.enterprise.{module}.{package};

public class {class_name} {{
    // Enterprise implementation
}}
'''
                self._create_file(file_path, code)

    # Methods for making changes and injecting bugs
    def _add_new_method(self, repo_path: Path):
        """Add a new method to a random file"""
        # Find a random source file
        source_files = list(repo_path.glob("**/*.py")) + list(repo_path.glob("**/*.java")) + list(repo_path.glob("**/*.js"))
        if not source_files:
            return
        
        file_path = random.choice(source_files)
        
        # Read existing content
        content = file_path.read_text()
        
        # Add a simple method
        if file_path.suffix == '.py':
            new_method = '''
def new_feature():
    """New feature implementation"""
    return "Feature implemented"
'''
        elif file_path.suffix == '.java':
            new_method = '''
    public String newFeature() {
        return "Feature implemented";
    }
'''
        else:  # JavaScript
            new_method = '''
function newFeature() {
    return "Feature implemented";
}
'''
        
        # Append the method
        file_path.write_text(content + new_method)

    def _modify_existing_method(self, repo_path: Path):
        """Modify an existing method"""
        # Implementation would modify existing code
        pass

    def _add_new_file(self, repo_path: Path):
        """Add a new file to the repository"""
        # Implementation would add new files
        pass

    def _update_config(self, repo_path: Path):
        """Update configuration files"""
        # Implementation would modify config files
        pass

    def _add_test(self, repo_path: Path):
        """Add a new test"""
        # Implementation would add test files
        pass

    # Bug injection methods
    def _inject_null_pointer_bug(self, repo_path: Path, bug_id: str):
        """Inject a null pointer bug"""
        # Find a suitable file
        java_files = list(repo_path.glob("**/*.java"))
        if java_files:
            file_path = random.choice(java_files)
            content = file_path.read_text()
            
            # Simple null pointer injection
            buggy_content = content.replace(
                "if (user != null)",
                f"// BUG_{bug_id}: Removed null check\n// if (user != null)"
            )
            
            if buggy_content != content:
                file_path.write_text(buggy_content)

    def _inject_off_by_one_bug(self, repo_path: Path, bug_id: str):
        """Inject an off-by-one error"""
        # Implementation would inject off-by-one errors
        pass

    def _inject_race_condition_bug(self, repo_path: Path, bug_id: str):
        """Inject a race condition bug"""
        # Implementation would remove synchronization
        pass

    def _inject_memory_leak_bug(self, repo_path: Path, bug_id: str):
        """Inject a memory leak"""
        # Implementation would prevent cleanup
        pass

    def _inject_api_misuse_bug(self, repo_path: Path, bug_id: str):
        """Inject an API misuse bug"""
        # Implementation would use deprecated methods
        pass

    def _generate_commit_message(self) -> str:
        """Generate a realistic commit message"""
        prefixes = ["feat", "fix", "refactor", "docs", "test", "chore"]
        actions = ["add", "update", "improve", "optimize", "enhance", "implement"]
        features = ["user authentication", "data validation", "error handling", "performance", "security", "UI components"]
        
        prefix = random.choice(prefixes)
        action = random.choice(actions)
        feature = random.choice(features)
        
        return f"{prefix}: {action} {feature}"

    def _create_file(self, path: Path, content: str):
        """Create a file with content"""
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)

    def _create_repo_metadata(self, repo_path: Path, repo_name: str, size_category: str, num_bugs: int):
        """Create metadata file for the repository"""
        metadata = {
            "repository_name": repo_name,
            "size_category": size_category,
            "num_bugs": num_bugs,
            "created_date": datetime.now().isoformat(),
            "bug_injection_commits": []  # Would be populated during generation
        }
        
        metadata_path = repo_path / ".mrr_metadata.json"
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)

    def _create_repos_metadata(self):
        """Create overall metadata for all repositories"""
        metadata = {
            "total_repositories": 65,
            "total_bugs": 7500,  # 50*10 + 100*30 + 150*20 + 200*5
            "repository_types": {
                "small": 10,
                "medium": 30,
                "large": 20,
                "enterprise": 5
            },
            "languages": ["python", "java", "javascript"],
            "frameworks": ["flask", "spring", "react"],
            "created_date": datetime.now().isoformat()
        }
        
        metadata_path = self.repos_path / "REPOSITORIES_METADATA.json"
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)


def main():
    """Main function to generate test repositories"""
    base_path = "/Users/ishraqkhan/Chronosss/Chronos/benchmarks/mrr_full_benchmark"
    generator = TestRepoGenerator(base_path)
    
    # Note: This would take a very long time to generate all repos
    # For demonstration, we'll create a subset
    print("Note: Full repository generation would create 65 repos with 7500 bugs.")
    print("This would require significant time and disk space.")
    print("\nTo generate all repositories, uncomment the line below:")
    # generator.generate_all_repos()
    
    # Instead, create a sample small repository for demonstration
    print("Creating a sample small repository for demonstration...")
    generator._generate_repository("sample_small_repo", "small", 5)
    print("✓ Created sample repository at test_repositories/sample_small_repo")


if __name__ == "__main__":
    main()