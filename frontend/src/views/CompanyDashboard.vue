<template>
  <div class="container mt-4 pb-5">
    <div class="d-flex justify-content-between align-items-center border-bottom pb-3 mb-4">
      <div><h4>Welcome {{ companyName }}</h4></div>
      <button @click="logout" class="btn btn-outline-danger btn-sm">logout</button>
    </div>

    <!-- WIREFRAME: Upcoming Drives / Create Drive -->
    <div class="row mb-4">
      <div class="col-12 d-flex justify-content-between align-items-center">
        <h5>Upcoming Drives</h5>
        <button class="btn btn-success btn-sm" data-bs-toggle="modal" data-bs-target="#createDriveModal">Create Drive</button>
      </div>
    </div>

    <div class="card shadow-sm mb-5">
      <table class="table table-hover mb-0 align-middle">
        <thead class="table-light">
          <tr><th>Sr No.</th><th>Drive Name</th><th>Actions</th></tr>
        </thead>
        <tbody>
          <tr v-for="(drive, index) in upcomingDrives" :key="drive.id">
            <td>{{ 1001 + index }}.</td>
            <td>{{ drive.title }}</td>
            <td>
              <button @click="loadApplications(drive)" class="btn btn-outline-primary btn-sm me-2">view details</button>
              <button class="btn btn-outline-success btn-sm">mark as complete</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- WIREFRAME: Update Applications for the Drive -->
    <div v-if="selectedDrive" class="card shadow p-4 mb-5 border-primary">
      <h5 class="mb-3 border-bottom pb-2">Update Applications for: {{ selectedDrive.title }}</h5>
      <p class="small text-muted">Job Title: {{ selectedDrive.title }}</p>
      
      <table class="table table-bordered">
        <thead class="table-light">
          <tr><th>Received Applications</th><th>Actions</th></tr>
        </thead>
        <tbody>
          <tr v-for="app in applicants" :key="app.id">
            <td>{{ app.student_name }}</td>
            <td>
              <div class="d-flex gap-2">
                <button @click="updateStatus(app.id, 'Shortlisted')" class="btn btn-warning btn-sm">Shortlist</button>
                <button @click="updateStatus(app.id, 'Waiting')" class="btn btn-info btn-sm">Waiting</button>
                <button @click="updateStatus(app.id, 'Rejected')" class="btn btn-danger btn-sm">Reject</button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
      <div class="text-end mt-3">
        <button @click="selectedDrive = null" class="btn btn-primary px-4">save</button>
      </div>
    </div>

    <!-- WIREFRAME: Create a Drive Modal -->
    <div class="modal fade" id="createDriveModal" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content shadow">
          <div class="modal-header"><h5>Create a Drive</h5></div>
          <div class="modal-body">
            <div class="mb-3"><label class="small">Drive Name</label><input v-model="newDrive.title" class="form-control"></div>
            <div class="mb-3"><label class="small">Job Description</label><textarea v-model="newDrive.desc" class="form-control" rows="3"></textarea></div>
            <div class="row">
              <div class="col-6 mb-3"><label class="small">Salary</label><input v-model="newDrive.salary" class="form-control" placeholder="e.g. 600000"></div>
              <div class="col-6 mb-3"><label class="small">Location</label><input v-model="newDrive.location" class="form-control" placeholder="e.g. Chennai"></div>
            </div>
            <div class="row">
              <div class="col-6 mb-3"><label class="small">Min CGPA</label><input v-model="newDrive.cgpa" type="number" step="0.1" class="form-control"></div>
              <div class="col-6 mb-3"><label class="small">Application Deadline</label><input v-model="newDrive.date" type="date" class="form-control"></div>
            </div>
          </div>
          <div class="modal-footer">
            <button @click="createDrive" class="btn btn-success px-4" data-bs-dismiss="modal">save</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
export default {
  data() {
    return {
      drives: [],
      applicants: [],
      selectedDrive: null,
      companyName: localStorage.getItem('name') || 'Organization',
      userId: localStorage.getItem('user_id'),
      newDrive: { title: '', desc: '', salary: '', location: '', cgpa: 0, date: '' }
    }
  },
  computed: {
    upcomingDrives() { return this.drives.filter(d => d.status !== 'Closed') }
  },
  methods: {
    async fetchDrives() {
      const res = await axios.get(`http://localhost:5000/api/company/drives/${this.userId}`)
      this.drives = res.data
    },
    async createDrive() {
      try {
        await axios.post(`http://localhost:5000/api/company/drives/${this.userId}`, {
          job_title: this.newDrive.title, description: this.newDrive.desc,
          salary: this.newDrive.salary, location: this.newDrive.location,
          min_cgpa: this.newDrive.cgpa, deadline: this.newDrive.date
        })
        this.fetchDrives()
      } catch (err) { alert(err.response.data.message) }
    },
    async loadApplications(drive) {
      this.selectedDrive = drive
      const res = await axios.get(`http://localhost:5000/api/drive/${drive.id}/applications`)
      this.applicants = res.data
    },
    async updateStatus(appId, status) {
      await axios.post(`http://localhost:5000/api/application/status`, { application_id: appId, status: status })
      this.loadApplications(this.selectedDrive)
    },
    logout() { localStorage.clear(); this.$router.push('/') }
  },
  mounted() { this.fetchDrives() }
}
</script>