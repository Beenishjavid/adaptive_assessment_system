-- =======================================================
-- ENHANCED SMART QUIZ SYSTEM - COMPLETE SQL SERVER DATABASE SCHEMA
-- =======================================================
-- Enhanced Version: 3.0 (Production Ready with Full Features)
-- Date: September 8, 2025
-- Description: Enhanced schema with all required features for Smart Quiz System

USE SmartQuizDB;
GO

-- =======================================================
-- ENHANCED TABLES FOR MISSING FEATURES
-- =======================================================

-- Organizations Table (Multi-tenant support)
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'organizations_organization')
CREATE TABLE organizations_organization (
    id BIGINT IDENTITY(1,1) PRIMARY KEY,
    name NVARCHAR(200) NOT NULL,
    domain NVARCHAR(100) NULL,
    description NVARCHAR(MAX),
    contact_email NVARCHAR(254) NULL,
    phone NVARCHAR(20) NULL,
    address NVARCHAR(MAX),
    is_active BIT NOT NULL DEFAULT 1,
    subscription_type NVARCHAR(20) NOT NULL DEFAULT 'basic' CHECK (subscription_type IN ('basic', 'premium', 'enterprise')),
    max_users INT DEFAULT 100,
    created_at DATETIME2 DEFAULT GETDATE(),
    updated_at DATETIME2 DEFAULT GETDATE()
);

-- Add organization_id to users_userprofile if not exists
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS 
               WHERE TABLE_NAME = 'users_userprofile' AND COLUMN_NAME = 'organization_id')
BEGIN
    ALTER TABLE users_userprofile ADD organization_id BIGINT NULL;
    ALTER TABLE users_userprofile ADD CONSTRAINT FK_userprofile_organization 
        FOREIGN KEY (organization_id) REFERENCES organizations_organization(id);
END

-- Enhanced Question Types (Add missing types to existing table)
IF EXISTS (SELECT * FROM INFORMATION_SCHEMA.CHECK_CONSTRAINTS 
           WHERE CONSTRAINT_NAME = 'CK__quizzes_q__quest__5BE2A6F2' 
           OR CONSTRAINT_NAME LIKE '%quizzes_question%question_type%')
BEGIN
    -- Drop existing constraint
    DECLARE @constraint_name NVARCHAR(128)
    SELECT @constraint_name = CONSTRAINT_NAME 
    FROM INFORMATION_SCHEMA.CHECK_CONSTRAINTS 
    WHERE TABLE_NAME = 'quizzes_question' AND COLUMN_NAME = 'question_type'
    
    IF @constraint_name IS NOT NULL
    BEGIN
        EXEC('ALTER TABLE quizzes_question DROP CONSTRAINT ' + @constraint_name)
    END
END

-- Add new constraint with all question types
ALTER TABLE quizzes_question ADD CONSTRAINT CK_question_type 
CHECK (question_type IN ('multiple_choice', 'true_false', 'short_answer', 'essay', 'matching'));

-- Add fields for enhanced question types
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS 
               WHERE TABLE_NAME = 'quizzes_question' AND COLUMN_NAME = 'explanation')
BEGIN
    ALTER TABLE quizzes_question ADD explanation NVARCHAR(MAX) NULL;
    ALTER TABLE quizzes_question ADD max_length INT NULL; -- For short answer questions
    ALTER TABLE quizzes_question ADD allow_partial_credit BIT DEFAULT 0;
END

-- Matching Questions Support
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'quizzes_matching_pair')
CREATE TABLE quizzes_matching_pair (
    id BIGINT IDENTITY(1,1) PRIMARY KEY,
    question_id BIGINT NOT NULL,
    left_item NVARCHAR(500) NOT NULL,
    right_item NVARCHAR(500) NOT NULL,
    [order] INT DEFAULT 0,
    FOREIGN KEY (question_id) REFERENCES quizzes_question(id) ON DELETE CASCADE
);

-- Enhanced Answer Support for different question types
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS 
               WHERE TABLE_NAME = 'results_answer' AND COLUMN_NAME = 'text_answer')
BEGIN
    ALTER TABLE results_answer ADD text_answer NVARCHAR(MAX) NULL; -- For short answer/essay
    ALTER TABLE results_answer ADD matching_pairs NVARCHAR(MAX) NULL; -- JSON for matching answers
    ALTER TABLE results_answer ADD points_earned FLOAT DEFAULT 0; -- For partial credit
END

-- Proctoring Events Table
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'proctoring_event')
CREATE TABLE proctoring_event (
    id BIGINT IDENTITY(1,1) PRIMARY KEY,
    attempt_id BIGINT NOT NULL,
    event_type NVARCHAR(50) NOT NULL CHECK (event_type IN ('tab_switch', 'window_blur', 'window_focus', 'fullscreen_exit', 'fullscreen_enter', 'copy_attempt', 'paste_attempt', 'right_click', 'key_combination', 'mouse_leave', 'mouse_enter')),
    event_data NVARCHAR(MAX), -- JSON data for additional info
    timestamp DATETIME2 DEFAULT GETDATE(),
    severity NVARCHAR(20) DEFAULT 'low' CHECK (severity IN ('low', 'medium', 'high', 'critical')),
    FOREIGN KEY (attempt_id) REFERENCES results_quizattempt(id) ON DELETE CASCADE
);

-- Email Templates Table
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'notifications_emailtemplate')
CREATE TABLE notifications_emailtemplate (
    id BIGINT IDENTITY(1,1) PRIMARY KEY,
    name NVARCHAR(100) NOT NULL UNIQUE,
    subject NVARCHAR(200) NOT NULL,
    html_content NVARCHAR(MAX) NOT NULL,
    text_content NVARCHAR(MAX),
    template_type NVARCHAR(50) NOT NULL CHECK (template_type IN ('quiz_completion', 'quiz_assignment', 'group_invitation', 'account_activation', 'password_reset')),
    is_active BIT DEFAULT 1,
    created_at DATETIME2 DEFAULT GETDATE(),
    updated_at DATETIME2 DEFAULT GETDATE()
);

-- Email Queue Table for background processing
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'notifications_emailqueue')
CREATE TABLE notifications_emailqueue (
    id BIGINT IDENTITY(1,1) PRIMARY KEY,
    recipient_email NVARCHAR(254) NOT NULL,
    subject NVARCHAR(200) NOT NULL,
    html_content NVARCHAR(MAX),
    text_content NVARCHAR(MAX),
    status NVARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'sent', 'failed', 'retry')),
    priority NVARCHAR(10) DEFAULT 'normal' CHECK (priority IN ('low', 'normal', 'high')),
    template_id BIGINT NULL,
    context_data NVARCHAR(MAX), -- JSON data for template variables
    attempts INT DEFAULT 0,
    max_attempts INT DEFAULT 3,
    last_error NVARCHAR(MAX),
    scheduled_at DATETIME2 DEFAULT GETDATE(),
    sent_at DATETIME2 NULL,
    created_at DATETIME2 DEFAULT GETDATE(),
    FOREIGN KEY (template_id) REFERENCES notifications_emailtemplate(id)
);

-- Quiz History View for Students
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'results_quizhistory')
CREATE TABLE results_quizhistory (
    id BIGINT IDENTITY(1,1) PRIMARY KEY,
    user_id INT NOT NULL,
    quiz_id BIGINT NOT NULL,
    attempt_id BIGINT NOT NULL,
    score INT NOT NULL,
    percentage FLOAT NOT NULL,
    passed BIT NOT NULL,
    completed_at DATETIME2 NOT NULL,
    time_taken_minutes INT,
    total_questions INT,
    correct_answers INT,
    wrong_answers INT,
    FOREIGN KEY (user_id) REFERENCES auth_user(id),
    FOREIGN KEY (quiz_id) REFERENCES quizzes_quiz(id),
    FOREIGN KEY (attempt_id) REFERENCES results_quizattempt(id)
);

-- =======================================================
-- INSERT ENHANCED CONTENT TYPES
-- =======================================================

-- Add new content types for enhanced features
INSERT INTO django_content_type (app_label, model) 
SELECT * FROM (VALUES
    ('organizations', 'organization'),
    ('proctoring', 'event'),
    ('quizzes', 'matchingpair'),
    ('notifications', 'emailtemplate'),
    ('notifications', 'emailqueue'),
    ('results', 'quizhistory')
) AS v(app_label, model)
WHERE NOT EXISTS (
    SELECT 1 FROM django_content_type dct 
    WHERE dct.app_label = v.app_label AND dct.model = v.model
);

-- =======================================================
-- ENHANCED INDEXES FOR PERFORMANCE
-- =======================================================

-- Organization indexes
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_organizations_organization_domain')
    CREATE INDEX IX_organizations_organization_domain ON organizations_organization(domain);

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_organizations_organization_active')
    CREATE INDEX IX_organizations_organization_active ON organizations_organization(is_active);

-- Enhanced question indexes
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_quizzes_question_type')
    CREATE INDEX IX_quizzes_question_type ON quizzes_question(question_type);

-- Matching pairs indexes
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_quizzes_matching_pair_question')
    CREATE INDEX IX_quizzes_matching_pair_question ON quizzes_matching_pair(question_id);

-- Proctoring event indexes
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_proctoring_event_attempt')
    CREATE INDEX IX_proctoring_event_attempt ON proctoring_event(attempt_id);

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_proctoring_event_type')
    CREATE INDEX IX_proctoring_event_type ON proctoring_event(event_type);

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_proctoring_event_timestamp')
    CREATE INDEX IX_proctoring_event_timestamp ON proctoring_event(timestamp);

-- Email queue indexes
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_notifications_emailqueue_status')
    CREATE INDEX IX_notifications_emailqueue_status ON notifications_emailqueue(status);

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_notifications_emailqueue_scheduled')
    CREATE INDEX IX_notifications_emailqueue_scheduled ON notifications_emailqueue(scheduled_at);

-- Quiz history indexes
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_results_quizhistory_user')
    CREATE INDEX IX_results_quizhistory_user ON results_quizhistory(user_id);

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_results_quizhistory_quiz')
    CREATE INDEX IX_results_quizhistory_quiz ON results_quizhistory(quiz_id);

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_results_quizhistory_completed')
    CREATE INDEX IX_results_quizhistory_completed ON results_quizhistory(completed_at);

-- =======================================================
-- ENHANCED STORED PROCEDURES
-- =======================================================

-- Enhanced procedure to handle different question types
GO
IF OBJECT_ID('dbo.sp_CalculateEnhancedQuizScore', 'P') IS NOT NULL
    DROP PROCEDURE dbo.sp_CalculateEnhancedQuizScore;
GO
CREATE PROCEDURE dbo.sp_CalculateEnhancedQuizScore
    @AttemptId BIGINT
AS
BEGIN
    DECLARE @Score FLOAT = 0;
    DECLARE @TotalMarks INT = 0;
    DECLARE @Percentage FLOAT;
    
    -- Calculate score including partial credit
    SELECT 
        @Score = ISNULL(SUM(
            CASE 
                WHEN q.question_type IN ('multiple_choice', 'true_false') 
                THEN CASE WHEN a.is_correct = 1 THEN q.marks ELSE 0 END
                ELSE ISNULL(a.points_earned, 0)
            END
        ), 0),
        @TotalMarks = ISNULL(SUM(q.marks), 0)
    FROM results_answer a
    INNER JOIN quizzes_question q ON a.question_id = q.id
    WHERE a.attempt_id = @AttemptId;
    
    -- Calculate percentage
    SET @Percentage = CASE WHEN @TotalMarks > 0 THEN (@Score * 100.0) / @TotalMarks ELSE 0 END;
    
    -- Update attempt record
    UPDATE results_quizattempt 
    SET score = @Score, 
        total_marks = @TotalMarks, 
        percentage = @Percentage
    WHERE id = @AttemptId;
    
    -- Insert into quiz history
    INSERT INTO results_quizhistory (user_id, quiz_id, attempt_id, score, percentage, passed, completed_at, time_taken_minutes, total_questions, correct_answers, wrong_answers)
    SELECT 
        qa.user_id,
        qa.quiz_id,
        qa.id,
        @Score,
        @Percentage,
        CASE WHEN @Percentage >= q.passing_score THEN 1 ELSE 0 END,
        qa.finished_at,
        qa.time_taken_minutes,
        (SELECT COUNT(*) FROM quizzes_question WHERE quiz_id = qa.quiz_id),
        (SELECT COUNT(*) FROM results_answer a INNER JOIN quizzes_question qu ON a.question_id = qu.id 
         WHERE a.attempt_id = @AttemptId AND a.is_correct = 1),
        (SELECT COUNT(*) FROM results_answer a INNER JOIN quizzes_question qu ON a.question_id = qu.id 
         WHERE a.attempt_id = @AttemptId AND a.is_correct = 0)
    FROM results_quizattempt qa
    INNER JOIN quizzes_quiz q ON qa.quiz_id = q.id
    WHERE qa.id = @AttemptId;
    
    SELECT @Score AS Score, @TotalMarks AS TotalMarks, @Percentage AS Percentage;
END;
GO

-- Procedure to queue completion email
GO
IF OBJECT_ID('dbo.sp_QueueCompletionEmail', 'P') IS NOT NULL
    DROP PROCEDURE dbo.sp_QueueCompletionEmail;
GO
CREATE PROCEDURE dbo.sp_QueueCompletionEmail
    @AttemptId BIGINT
AS
BEGIN
    DECLARE @UserEmail NVARCHAR(254);
    DECLARE @QuizTitle NVARCHAR(200);
    DECLARE @Score FLOAT;
    DECLARE @Percentage FLOAT;
    DECLARE @TemplateId BIGINT;
    
    -- Get attempt details
    SELECT 
        @UserEmail = u.email,
        @QuizTitle = q.title,
        @Score = qa.score,
        @Percentage = qa.percentage
    FROM results_quizattempt qa
    INNER JOIN auth_user u ON qa.user_id = u.id
    INNER JOIN quizzes_quiz q ON qa.quiz_id = q.id
    WHERE qa.id = @AttemptId;
    
    -- Get template
    SELECT @TemplateId = id FROM notifications_emailtemplate 
    WHERE template_type = 'quiz_completion' AND is_active = 1;
    
    -- Queue email
    INSERT INTO notifications_emailqueue (recipient_email, subject, template_id, context_data, priority)
    VALUES (
        @UserEmail,
        'Quiz Completion - ' + @QuizTitle,
        @TemplateId,
        '{"quiz_title":"' + @QuizTitle + '","score":"' + CAST(@Score AS NVARCHAR) + '","percentage":"' + CAST(@Percentage AS NVARCHAR) + '","attempt_id":"' + CAST(@AttemptId AS NVARCHAR) + '"}',
        'normal'
    );
END;
GO

-- =======================================================
-- INSERT DEFAULT EMAIL TEMPLATES
-- =======================================================

-- Insert default email templates
INSERT INTO notifications_emailtemplate (name, subject, html_content, text_content, template_type) VALUES
('Quiz Completion Default', 'Quiz Results - {{quiz_title}}', 
'<html>
<body style="font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5;">
    <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
        <h2 style="color: #333; text-align: center; margin-bottom: 30px;">Quiz Completion Report</h2>
        <div style="background-color: #f8f9fa; padding: 20px; border-radius: 5px; margin-bottom: 20px;">
            <h3 style="color: #495057; margin-top: 0;">Quiz: {{quiz_title}}</h3>
            <p style="font-size: 18px; margin: 10px 0;"><strong>Your Score:</strong> {{score}} points</p>
            <p style="font-size: 18px; margin: 10px 0;"><strong>Percentage:</strong> {{percentage}}%</p>
            <p style="font-size: 16px; color: {{status_color}}; margin: 10px 0;"><strong>Status:</strong> {{status}}</p>
        </div>
        <div style="margin-top: 30px;">
            <h4 style="color: #333;">Answer Summary:</h4>
            <div style="background-color: #e9ecef; padding: 15px; border-radius: 5px;">
                <p style="margin: 5px 0;">Total Questions: {{total_questions}}</p>
                <p style="margin: 5px 0; color: #28a745;">Correct Answers: {{correct_answers}}</p>
                <p style="margin: 5px 0; color: #dc3545;">Wrong Answers: {{wrong_answers}}</p>
            </div>
        </div>
        <div style="text-align: center; margin-top: 30px;">
            <a href="{{quiz_url}}" style="background-color: #007bff; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block;">View Detailed Results</a>
        </div>
        <p style="text-align: center; color: #6c757d; font-size: 14px; margin-top: 30px;">
            This is an automated email from Smart Quiz System. Please do not reply.
        </p>
    </div>
</body>
</html>',
'Quiz Completion Report

Quiz: {{quiz_title}}
Your Score: {{score}} points
Percentage: {{percentage}}%
Status: {{status}}

Answer Summary:
- Total Questions: {{total_questions}}
- Correct Answers: {{correct_answers}}
- Wrong Answers: {{wrong_answers}}

View your detailed results at: {{quiz_url}}

This is an automated email from Smart Quiz System.',
'quiz_completion');

PRINT 'Enhanced Smart Quiz System schema created successfully!';
PRINT 'New Features Added:';
PRINT '✅ Multi-tenant Organization support';
PRINT '✅ Enhanced Question Types (MCQ, True/False, Short Answer, Essay, Matching)';
PRINT '✅ Comprehensive Proctoring System (SmartMonitor)';
PRINT '✅ Advanced Email System with Templates and Queue';
PRINT '✅ Quiz History and Analytics';
PRINT '✅ Partial Credit Support';
PRINT '✅ Enhanced Performance Indexes';
PRINT '';
PRINT 'Question Types Supported:';
PRINT '- Multiple Choice (single/multi-select)';
PRINT '- True/False';
PRINT '- Short Answer';
PRINT '- Essay';
PRINT '- Matching';
PRINT '';
PRINT 'Proctoring Events Tracked:';
PRINT '- Tab switches';
PRINT '- Window focus/blur';
PRINT '- Fullscreen changes';
PRINT '- Copy/paste attempts';
PRINT '- Right-click events';
PRINT '- Mouse leave/enter';
PRINT '- Key combinations';
PRINT '';
PRINT 'Email Features:';
PRINT '- Background email processing';
PRINT '- Template-based emails';
PRINT '- Automatic quiz completion emails';
PRINT '- Retry mechanism for failed emails';
PRINT '';
PRINT 'Database is now ready for the Smart Quiz System implementation!';
