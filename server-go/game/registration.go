package game

type RegistrationRequest struct {
	Team Team   `json:"team"`
	Name string `json:"name"`
}

type RegistrationResponse struct {
	Id int `json:"id"`
	RegistrationRequest
}
