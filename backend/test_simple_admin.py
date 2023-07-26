#!/usr/bin/env python3
"""
Simple Admin API Test
"""
import requests
import json

def test_admin_apis():
    print("Testing Admin APIs...")
    
    try:
        # Login as admin
        response = requests.post(
            'http://127.0.0.1:8000/api/auth/login/', 
            json={'username': 'admin', 'password': 'admin123'},
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            token_data = response.json()
            token = token_data.get('access')
            headers = {'Authorization': f'Bearer {token}'}
            
            print("✅ Admin login successful")
            
            # Test users endpoint
            users_resp = requests.get('http://127.0.0.1:8000/api/admin/users/', headers=headers)
            if users_resp.status_code == 200:
                users_data = users_resp.json()
                print(f"✅ Users API: {len(users_data.get('users', []))} users found")
            else:
                print(f"❌ Users API failed: {users_resp.status_code}")
                print(f"Error: {users_resp.text}")
            
            # Test organizations endpoint  
            orgs_resp = requests.get('http://127.0.0.1:8000/api/admin/organizations/', headers=headers)
            if orgs_resp.status_code == 200:
                orgs_data = orgs_resp.json()
                print(f"✅ Organizations API: {len(orgs_data.get('organizations', []))} organizations found")
            else:
                print(f"❌ Organizations API failed: {orgs_resp.status_code}")
                print(f"Error: {orgs_resp.text}")
                
            # Test user stats endpoint
            stats_resp = requests.get('http://127.0.0.1:8000/api/admin/stats/', headers=headers)
            if stats_resp.status_code == 200:
                stats_data = stats_resp.json()
                print(f"✅ User Stats API: {stats_data.get('total_users', 0)} total users")
            else:
                print(f"❌ User Stats API failed: {stats_resp.status_code}")
                print(f"Error: {stats_resp.text}")
                
            # Test system overview
            overview_resp = requests.get('http://127.0.0.1:8000/api/admin/system-overview/', headers=headers)
            if overview_resp.status_code == 200:
                overview_data = overview_resp.json()
                print(f"✅ System Overview API: Working")
                print(f"   Users: {overview_data.get('users', {}).get('total', 0)}")
                print(f"   Quizzes: {overview_data.get('quizzes', {}).get('total', 0)}")
            else:
                print(f"❌ System Overview API failed: {overview_resp.status_code}")
                print(f"Error: {overview_resp.text}")
                
        else:
            print(f"❌ Admin login failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Test error: {e}")

if __name__ == "__main__":
    test_admin_apis()
