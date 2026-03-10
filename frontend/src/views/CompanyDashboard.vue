<template>
  <div class="container mt-4 pb-5">
    <!-- TOP BAR -->
    <div class="d-flex justify-content-between align-items-center border-bottom pb-2 mb-4">
      <h5 class="mb-0 text-muted">Welcome <span class="text-dark fw-bold">{{ companyName }}</span></h5>
      <button @click="logout" class="btn btn-link text-danger text-decoration-none small">logout</button>
    </div>

    <!-- VIEW 1: MAIN DASHBOARD (Upcoming & Closed Tables) -->
    <div v-if="view === 'main'">
      <div class="d-flex justify-content-between align-items-center mb-3">
        <h6 class="fw-bold">Upcoming Drives</h6>
        <button class="btn btn-success btn-sm px-4 shadow-sm" @click="prepareCreate" data-bs-toggle="modal" data-bs-target="#driveModal">Create Drive</button>
      </div>
      
      <!-- Table: Upcoming -->
      <div class="card shadow-sm mb-4 border-0">
        <table class="table table-bordered mb-0 align-middle text-center small">
          <thead class="table-light">
            <tr><th>Sr No.</th><th>Drive Name</th><th>Actions</th></tr>
          </thead>
          <tbody>
            <tr v-for="(d, idx) in upcoming" :key="d.id">
              <td>{{ 1001 + idx }}.</td>
              <td class="fw-bold">{{ d.title }}</td>
              <td>
                <button @click="openApplicants(d)" class="btn btn-outline-primary btn-sm me-2">view details</button>
                <button @click="editDrive(d)" class="btn btn-outline-warning btn-sm me-2" data-bs-toggle="modal" data-bs-target="#driveModal">edit</button>
                <button @click="deleteDrive(d.id)" class="btn btn-outline-danger btn-sm me-2">delete</button>
                <button @click="markComplete(d.id)" class="btn btn-outline-success btn-sm">mark as complete</button>
              </td>
            </tr>
            <tr v-if="upcoming.length === 0"><td colspan="3" class="py-4 text-muted">No upcoming drives. Create one to start hiring.</td></tr>
          </tbody>
        </table>
      </div>

      <h6 class="fw-bold">Closed Drives</h6>
      <!-- Table: Closed -->
      <div class="card shadow-sm border-0">
        <table class="table table-bordered mb-0 align-middle text-center small">
          <thead class="table-light">
            <tr><th>Sr No.</th><th>Drive Name</th><th>Actions</th></tr>
          </thead>
          <tbody>
            <tr v-for="(d, idx) in closed" :key="d.id">
              <td>{{ 1011 + idx }}.</td>
              <td>{{ d.title }}</td>
              <td><button @click="openApplicants(d)" class="btn btn-outline-secondary btn-sm">update / view results</button></td>
            </tr>
            <tr v-if="closed.length === 0"><td colspan="3" class="py-4 text-muted">No closed drives yet.</td></tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- VIEW 2: APPLICANT LIST (With CGPA Filter) -->
    <div v-if="view === 'applicants'" class="card shadow p-4 border-0">
      <div class="d-flex justify-content-between align-items-center mb-3 border-bottom pb-2">
        <div>
           <h5 class="mb-0">Update Applications for the Drive</h5>
           <p class="text-muted small mb-0">Job Title: <strong>{{ selectedDrive.title }}</strong></p>
        </div>
        <div class="d-flex align-items-center gap-2">
           <label class="small text-nowrap">Min CGPA Filter:</label>
           <input v-model.number="cgpaFilter" type="number" step="0.1" class="form-control form-control-sm" style="width:80px">
        </div>
      </div>

      <table class="table table-bordered align-middle text-center small">
        <thead class="table-light"><tr><th>Received Applications</th><th>Current Status</th><th>Actions</th></tr></thead>
        <tbody>
          <tr v-for="a in filteredApps" :key="a.id">
            <td class="text-start">{{ a.student_name }} ({{ a.cgpa }} CGPA)</td>
            <td><span class="badge" :class="getBadge(a.status)">{{ a.status }}</span></td>
            <td><button @click="reviewStudent(a)" class="btn btn-outline-primary btn-sm px-3">review application</button></td>
          </tr>
          <tr v-if="filteredApps.length === 0"><td colspan="3" class="py-4 text-muted">No applicants found matching filter.</td></tr>
        </tbody>
      </table>
      <div class="text-end mt-4">
        <button @click="view = 'main'" class="btn btn-success px-5">save & back</button>
      </div>
    </div>

    <!-- VIEW 3: INDIVIDUAL STUDENT REVIEW (Drill-down) -->
    <div v-if="view === 'review'" class="card shadow p-4 border-0">
      <div class="row align-items-center">
        <div class="col-md-8">
          <h3 class="mb-4">Student Application</h3>
          <p class="mb-1"><strong>Student Name:</strong> {{ activeApp.student_name }}</p>
          <p class="mb-1"><strong>Department:</strong> {{ activeApp.department }}</p>
          <p class="mb-1"><strong>Applied for Drive:</strong> {{ selectedDrive.title }}</p>
          <p class="mb-1"><strong>Current CGPA:</strong> {{ activeApp.cgpa }}</p>
          
          <div class="mt-4 pt-3 border-top d-flex align-items-center gap-3">
            <a :href="activeApp.resume" target="_blank" class="btn btn-outline-primary btn-sm px-3">view resume</a>
            <select v-model="activeApp.status" @change="updateAppStatus(activeApp.id, activeApp.status)" class="form-select form-select-sm" style="width:200px">
               <option value="Applied">v Choose Status</option>
               <option value="Shortlisted">Shortlist</option>
               <option value="Waiting">Waiting</option>
               <option value="Rejected">Reject</option>
               <option value="Selected">Select</option>
            </select>
          </div>
        </div>
        <div class="col-md-4 text-center">
          <div class="rounded-circle bg-light border d-flex align-items-center justify-content-center mx-auto" style="width:180px; height:180px">
              <span class="text-muted">PHOTO</span>
          </div>
        </div>
      </div>
      <div class="text-end mt-5 border-top pt-3">
        <button @click="view = 'applicants'" class="btn btn-outline-secondary px-4">back to list</button>
      </div>
    </div>

    <!-- MODAL: CREATE / EDIT DRIVE -->
    <div class="modal fade" id="driveModal" tabindex="-1" aria-hidden="true">
      <div class="modal-dialog modal-lg">
        <div class="modal-content shadow border-0 p-3">
          <div class="modal-header border-0"><h5 class="modal-title fw-bold">{{ isEdit ? 'Update Drive Details' : 'Create a New Drive' }}</h5></div>
          <div class="modal-body">
            <div class="mb-3"><label class="small fw-bold">Drive Name / Job Title</label><input v-model="form.job_title" class="form-control" placeholder="e.g. Software Engineer"></div>
            <div class="mb-3"><label class="small fw-bold">Job Description</label><textarea v-model="form.description" class="form-control" rows="3" placeholder="Provide roles and responsibilities..."></textarea></div>
            <div class="row">
              <div class="col-6 mb-3"><label class="small fw-bold">Salary (CTC)</label><input v-model="form.salary" class="form-control" placeholder="e.g. 8,50,000"></div>
              <div class="col-6 mb-3"><label class="small fw-bold">Location</label><input v-model="form.location" class="form-control" placeholder="e.g. Bangalore, Remote"></div>
            </div>
            <div class="row">
              <div class="col-6 mb-3"><label class="small fw-bold">Min CGPA Criteria</label><input v-model.number="form.min_cgpa" type="number" step="0.1" class="form-control"></div>
              <div class="col-6 mb-3"><label class="small fw-bold">Application Deadline</label><input v-model="form.deadline" type="date" class="form-control"></div>
            </div>
          </div>
          <div class="modal-footer border-0">
            <button @click="submitDrive" class="btn btn-success w-100 py-2" data-bs-dismiss="modal">save drive</button>
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
      view: 'main',
      drives: [],
      apps: [],
      selectedDrive: {},
      activeApp: {},
      cgpaFilter: 0,
      isEdit: false,
      companyName: localStorage.getItem('name') || 'Organization',
      userId: localStorage.getItem('user_id'),
      form: { id: null, job_title: '', description: '', min_cgpa: 0, salary: '', location: '', deadline: '' }
    }
  },
  computed: {
    upcoming() { return this.drives.filter(d => d.status !== 'Closed') },
    closed() { return this.drives.filter(d => d.status === 'Closed') },
    filteredApps() { return this.apps.filter(a => a.cgpa >= this.cgpaFilter) }
  },
  methods: {
    async fetchDrives() {
      if (!this.userId) { this.$router.push('/'); return; }
      try {
        const res = await axios.get(`http://localhost:5000/api/company/drives/${this.userId}`)
        this.drives = res.data
      } catch (err) { console.error("Session sync failed.") }
    },
    prepareCreate() {
      this.isEdit = false
      this.form = { job_title: '', description: '', min_cgpa: 0, salary: '', location: '', deadline: '' }
    },
    async submitDrive() {
      try {
        if (this.isEdit) {
          await axios.put(`http://localhost:5000/api/company/drive/${this.form.id}`, this.form)
        } else {
          await axios.post(`http://localhost:5000/api/company/drives/${this.userId}`, this.form)
        }
        alert("Drive saved successfully!")
        this.fetchDrives()
      } catch (err) { alert(err.response?.data?.message || "Error saving drive.") }
    },
    editDrive(d) {
      this.isEdit = true
      this.form = { id: d.id, job_title: d.title, description: d.description, min_cgpa: d.min_cgpa, salary: d.salary, location: d.location, deadline: d.deadline }
    },
    async deleteDrive(id) {
      if (!confirm("Are you sure? This will also remove all applications for this drive.")) return
      try {
        await axios.delete(`http://localhost:5000/api/company/drive/${id}`)
        this.fetchDrives()
      } catch (err) { alert("Error deleting.") }
    },
    async markComplete(id) {
      if (!confirm("Marking as complete will close this drive for all students. Continue?")) return
      try {
        await axios.put(`http://localhost:5000/api/company/drive/${id}/status`, { status: 'Closed' })
        this.fetchDrives()
      } catch (err) { alert("Error closing drive.") }
    },
    async openApplicants(d) {
      this.selectedDrive = d
      try {
        const res = await axios.get(`http://localhost:5000/api/drive/${d.id}/applications`)
        this.apps = res.data
        this.view = 'applicants'
      } catch (err) { alert("Error loading applicants.") }
    },
    reviewStudent(app) {
      this.activeApp = app
      this.view = 'review'
    },
    async updateAppStatus(id, status) {
      try {
        await axios.post(`http://localhost:5000/api/application/status`, { application_id: id, status: status })
      } catch (err) { alert("Status update failed.") }
    },
    getBadge(s) {
      if(s==='Selected') return 'bg-success';
      if(s==='Rejected') return 'bg-danger';
      return 'bg-warning text-dark';
    },
    logout() { localStorage.clear(); this.$router.push('/') }
  },
  mounted() { this.fetchDrives() }
}
</script>