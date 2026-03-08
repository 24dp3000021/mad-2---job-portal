<template>
  <div class="container mt-4 pb-5">
    <!-- NAVBAR (Wireframe Top Bar) -->
    <div class="d-flex justify-content-between align-items-center border-bottom pb-3 mb-4">
      <div>
        <h4 class="mb-0">Welcome {{ profile.name }}</h4>
      </div>
      <div class="nav-links">
        <button @click="view = 'home'" class="btn btn-link text-dark">Home</button> |
        <button @click="view = 'profile'" class="btn btn-link text-dark">Edit Profile</button> |
        <button @click="view = 'history'" class="btn btn-link text-dark">History</button> |
        <button @click="logout" class="btn btn-link text-danger">Logout</button>
      </div>
    </div>

    <!-- VIEW 1: MAIN DASHBOARD (Organizations & Applied Drives) -->
    <div v-if="view === 'home'">
      <div class="row">
        <!-- Organizations Section -->
        <div class="col-12 mb-5">
          <h5 class="text-muted mb-3">Organizations</h5>
          <div v-for="org in companies" :key="org.id" class="card mb-2 border shadow-sm">
            <div class="card-body d-flex justify-content-between align-items-center">
              <span>{{ org.name }}</span>
              <button @click="showOrgDrives(org)" class="btn btn-outline-primary btn-sm">view details</button>
            </div>
          </div>
        </div>

        <!-- Applied Drives Section -->
        <div class="col-12">
          <h5 class="text-muted mb-3">Applied Drives</h5>
          <table class="table table-bordered bg-white shadow-sm">
            <thead class="table-light">
              <tr><th>Sr No.</th><th>Drive Name</th><th>Company</th><th>Date</th><th>Action</th></tr>
            </thead>
            <tbody>
              <tr v-for="(app, index) in history" :key="index">
                <td>{{ index + 1 }}</td>
                <td>{{ app.drive_title }}</td>
                <td>{{ app.company }}</td>
                <td>{{ app.date }}</td>
                <td><button @click="view = 'history'" class="btn btn-outline-primary btn-sm">view details</button></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- VIEW 2: EDIT PROFILE -->
    <div v-if="view === 'profile'" class="row justify-content-center">
      <div class="col-md-6 card shadow p-4">
        <h5>Edit Detailed Profile</h5>
        <div class="mb-3"><label>Full Name</label><input v-model="profile.name" class="form-control" disabled></div>
        <div class="mb-3">
            <label>Department</label>
            <select v-model="profile.department" class="form-select">
                <option>Computer Science</option><option>Electronics</option><option>Mechanical</option>
            </select>
        </div>
        <div class="mb-3"><label>CGPA</label><input v-model="profile.cgpa" type="number" step="0.01" class="form-control"></div>
        <div class="mb-3"><label>Resume Link (File Path)</label><input v-model="profile.resume" type="text" class="form-control" placeholder="Upload path/URL"></div>
        <button @click="updateProfile" class="btn btn-primary w-100">Save Changes</button>
        <button @click="view = 'home'" class="btn btn-link w-100 mt-2">Back to Dashboard</button>
      </div>
    </div>

    <!-- VIEW 3: DRIVE DETAILS (Matching Drive 1 Card in Wireframe) -->
    <div v-if="view === 'drive_details'" class="row justify-content-center">
      <div class="col-md-8 card shadow p-4">
        <div class="d-flex justify-content-between">
            <div>
                <h3>{{ selectedDrive.title }}</h3>
                <h5 class="text-muted">{{ selectedDrive.company_name }}</h5>
                <p class="mt-4">{{ selectedDrive.description }}</p>
                <p><strong>Salary:</strong> {{ selectedDrive.salary || 'Competitive' }}</p>
                <p><strong>Location:</strong> {{ selectedDrive.location || 'Remote' }}</p>
            </div>
            <div class="text-center">
                <div class="rounded-circle bg-info mb-2" style="width:80px; height:80px; margin:auto"></div>
                <small>COMPANY LOGO</small>
            </div>
        </div>
        <div class="mt-4 border-top pt-3 d-flex gap-2">
            <button @click="apply(selectedDrive.id)" class="btn btn-primary px-4">Apply</button>
            <button @click="view = 'home'" class="btn btn-outline-secondary px-4">Go Back</button>
        </div>
      </div>
    </div>

    <!-- VIEW 4: HISTORY (Wireframe Right-Top Card) -->
    <div v-if="view === 'history'">
      <div class="card shadow p-4 border-0">
        <div class="d-flex justify-content-between align-items-start mb-4">
            <div>
                <h4>Student Application History</h4>
                <p class="mb-0"><strong>Student Name:</strong> {{ profile.name }}</p>
                <p><strong>Department:</strong> {{ profile.department }}</p>
            </div>
            <button @click="view = 'home'" class="btn btn-outline-primary btn-sm">back</button>
        </div>
        <table class="table table-bordered text-center align-middle">
            <thead class="table-light">
                <tr><th>Drive No.</th><th>Status</th><th>Job Title</th><th>Results</th><th>Remark</th></tr>
            </thead>
            <tbody>
                <tr v-for="(app, index) in history" :key="index">
                    <td>{{ index + 1 }}</td>
                    <td>Online</td>
                    <td>{{ app.drive_title }}</td>
                    <td><span class="badge" :class="app.status === 'Selected' ? 'bg-success' : 'bg-info text-dark'">{{ app.status }}</span></td>
                    <td>None</td>
                </tr>
            </tbody>
          </table>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
export default {
  data() {
    return {
      view: 'home',
      profile: { name: '', cgpa: 0, resume: '', department: '' },
      companies: [],
      drives: [],
      history: [],
      selectedDrive: {},
      userId: localStorage.getItem('user_id')
    }
  },
  methods: {
    async loadData() {
      const [p, c, h, d] = await Promise.all([
        axios.get(`http://localhost:5000/api/student/profile/${this.userId}`),
        axios.get(`http://localhost:5000/api/student/companies`),
        axios.get(`http://localhost:5000/api/student/history/${this.userId}`),
        axios.get(`http://localhost:5000/api/student/drives`)
      ]);
      this.profile = p.data;
      this.companies = c.data;
      this.history = h.data;
      this.drives = d.data;
    },
    showOrgDrives(org) {
        // Logic to find drives for this specific company
        const drive = this.drives.find(d => d.company_name === org.name);
        if(drive) {
            this.selectedDrive = drive;
            this.view = 'drive_details';
        } else {
            alert("No active drives for this organization.");
        }
    },
    async updateProfile() {
      await axios.put(`http://localhost:5000/api/student/profile/${this.userId}`, { 
          cgpa: this.profile.cgpa, resume_link: this.profile.resume, department: this.profile.department 
      });
      alert("Profile Saved!");
      this.loadData();
      this.view = 'home';
    },
    async apply(id) {
      try {
        await axios.put(`http://localhost:5000/api/student/profile/${this.userId}`, { cgpa: this.profile.cgpa });
        const res = await axios.post(`http://localhost:5000/api/student/apply`, { user_id: this.userId, drive_id: id });
        alert(res.data.message);
        this.loadData();
        this.view = 'home';
      } catch (err) { alert(err.response.data.message); }
    },
    logout() { localStorage.clear(); this.$router.push('/'); }
  },
  mounted() { this.loadData(); }
}
</script>