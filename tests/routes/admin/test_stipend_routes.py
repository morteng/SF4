def test_create_stipend_route_htmx(client, admin_user, htmx_headers):
    # Test HTMX create stipend route
    login_response = client.post('/login', data={
        'username': admin_user.username,
        'password': 'admin_password'
    })
    assert login_response.status_code == 302
    
    # Create stipend with HTMX headers
    response = client.post('/admin/stipends/create', 
        headers=htmx_headers,
        data={
            'name': 'Test Stipend',
            'summary': 'Test Summary',
            'description': 'Test Description',
            'homepage_url': 'http://example.com',
            'application_procedure': 'Apply online',
            'eligibility_criteria': 'Open to all',
            'application_deadline': '2025-01-01 00:00:00',
            'organization_id': 1,
            'open_for_applications': True
        }
    )
    
    # Verify HTMX response
    assert response.status_code == 200
    # Verify template rendered correctly
    assert b"Test Stipend" in response.data
    # Verify flash message in response
    assert b"Stipend created successfully" in response.data
