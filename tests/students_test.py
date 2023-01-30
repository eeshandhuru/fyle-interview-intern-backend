def test_get_assignments_student_1(client, h_student_1):
    response = client.get(
        '/student/assignments',
        headers=h_student_1
    )
    
    assert response.status_code == 200

    data = response.json['data']
    for assignment in data:
        assert assignment['student_id'] == 1


def test_get_assignments_student_2(client, h_student_2):
    response = client.get(
        '/student/assignments',
        headers=h_student_2
    )

    assert response.status_code == 200

    data = response.json['data']
    for assignment in data:
        assert assignment['student_id'] == 2


def test_post_assignment_student_1(client, h_student_1):
    content = 'ABCD TESTPOST'

    response = client.post(
        '/student/assignments',
        headers=h_student_1,
        json={
            'content': content
        })

    assert response.status_code == 200

    data = response.json['data']
    assert data['content'] == content
    assert data['state'] == 'DRAFT'
    assert data['teacher_id'] is None


def test_edit_assignment_student_1(client, h_student_1):
    content = None

    response = client.post(
        '/student/assignments',
        headers=h_student_1,
        json={
            'id': 5,
            'content': content
        })

    assert response.status_code == 200
    data = response.json['data']
    assert data['content'] == content
    assert data['state'] == 'DRAFT'
    assert data['teacher_id'] is None


def test_edit_assignment_bad_assignment(client, h_student_1):
    """
    failure case: If an assignment does not exist check and throw 404
    """
    content = 'IMAGINARY'
    
    response = client.post(
        '/student/assignments',
        headers=h_student_1,
        json={
            'id': 10000,
            'content': content
        })
    
    assert response.status_code == 404
    error_response = response.json
    assert error_response['error'] == 'FyleError'
    assert error_response['message'] == 'No assignment with this id was found'


def test_edit_assignment_other_student(client, h_student_2):
    """
    failure case: assignment 5 can only be edited by student 1 and not student 2
    """
    response = client.post(
        '/student/assignments',
        headers=h_student_2,
        json={
            'id': 5,
            'teacher_id': 1
        })
    error_response = response.json
    assert response.status_code == 400
    assert error_response['error'] == 'ValidationError'


def test_edit_assignment_submitted_assignment(client, h_student_1):
    """
    failure case: only a draft assignment can be edited
    """
    content = 'REPORT'

    response = client.post(
        '/student/assignments',
        headers=h_student_1,
        json={
            'id': 1,
            'content': content
        })

    assert response.status_code == 400
    error_response = response.json
    assert error_response['error'] == 'FyleError'
    assert error_response['message'] == 'only assignment in draft state can be edited'


def test_submit_assignment_student_1(client, h_student_1):
    response = client.post(
        '/student/assignments/submit',
        headers=h_student_1,
        json={
            'id': 2,
            'teacher_id': 2
        })

    assert response.status_code == 200

    data = response.json['data']
    assert data['student_id'] == 1
    assert data['state'] == 'SUBMITTED'
    assert data['teacher_id'] == 2


def test_submit_assignment_bad_assignment(client, h_student_1):
    """
    failure case: If an assignment does not exist check and throw 404
    """
    response = client.post(
        '/student/assignments/submit',
        headers=h_student_1,
        json={
            'id': 10000,
            'teacher_id': 2
        })
    error_response = response.json
    assert response.status_code == 404
    assert error_response['error'] == 'FyleError'
    assert error_response['message'] == 'No assignment with this id was found'


def test_submit_assignment_other_student(client, h_student_2):
    """
    failure case: assignment 5 can only be submitted by student 1 and not student 2
    """
    response = client.post(
        '/student/assignments/submit',
        headers=h_student_2,
        json={
            'id': 5,
            'teacher_id': 1
        })
    error_response = response.json
    assert response.status_code == 400
    assert error_response['error'] == 'FyleError'
    assert error_response['message'] == 'This assignment belongs to some other student'


def test_submit_empty_assignment(client, h_student_1):
    """
    failure case: An empty assignment cannot be graded
    """
    response = client.post(
        '/student/assignments/submit',
        headers=h_student_1,
        json={
            'id': 5,
            'teacher_id': 1
        })
    error_response = response.json
    assert response.status_code == 400
    assert error_response['error'] == 'FyleError'
    assert error_response['message'] == 'assignment with empty content cannot be submitted'

    
def test_assignment_resubmit_error(client, h_student_1):
    """
    failure case: a submitted assignment cannot be resubmitted
    """
    response = client.post(
        '/student/assignments/submit',
        headers=h_student_1,
        json={
            'id': 2,
            'teacher_id': 2
        })
    error_response = response.json
    assert response.status_code == 400
    assert error_response['error'] == 'FyleError'
    assert error_response["message"] == 'only a draft assignment can be submitted'
