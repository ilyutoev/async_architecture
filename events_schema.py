schema = {
  "v1": {

    "AccountCreated": {
      "type": "object",
      "properties": {
        "version": {"type": "string"},
        "event_name": {"type": "string"},
        "data": {
          "type":  "object",
          "properties": {
            "public_id": {"type":  "string"},
            "role": {"type":  "string"},
            "email": {"type":  "string"},
            'first_name': {"type":  "string"},
          }
        }
      }
    },

    "AccountDeleted": {
      "type": "object",
      "properties": {
        "version": {"type": "string"},
        "event_name": {"type": "string"},
        "data": {
          "type":  "object",
          "properties": {
            "public_id": {"type":  "string"}
          }
        }
      }
    },

    "AccountUpdated": {
      "type": "object",
      "properties": {
        "version": {"type": "string"},
        "event_name": {"type": "string"},
        "data": {
          "type":  "object",
          "properties": {
            "public_id": {"type":  "string"},
            "email": {"type":  "string"},
            'first_name': {"type":  "string"}
          }
        }
      }
    },

    "AccountRoleChanged": {
      "type": "object",
      "properties": {
        "version": {"type": "string"},
        "event_name": {"type": "string"},
        "data": {
          "type":  "object",
          "properties": {
            "public_id": {"type":  "string"},
            "role": {"type":  "string"}
          }
        }
      }
    }

  }
}