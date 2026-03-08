<template>
  <div class="container mt-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2>Admin Dashboard</h2>
      <button @click="logout" class="btn btn-outline-danger">Logout</button>
    </div>

    <!-- Stats Cards -->
    <div class="row mb-4">
      <div class="col-md-3" v-for="(val, key) in stats" :key="key">
        <div class="card text-center bg-light shadow-sm">
          <div class="card-body">
            <h6 class="text-uppercase text-muted">{{ key.replace('_', ' ') }}</h6>
            <h3>{{ val }}</h3>
          </div>
        </div>
      </div>
    </div>

    <!-- Tabs for Management -->
    <ul class="nav nav-tabs mb-3">
      <li class="nav-item" v-for="tab in ['companies', 'students', 'drives']" :key="tab">
        <button class="nav-link text-capitalize" :class="{active: activeTab === tab}" @click="fetchData(tab)">{{ tab }}</button>
      </li>
    </ul>

    <!-- Data Table -->
    <div class="card shadow-sm">
      <div class="table-responsive">
        <table class="table table-hover align-middle mb-0">
          <thead class="table-dark">
            <tr v-if="activeTab === 'companies'">
              <th>Name</th><th>Email</th><th>Status</th><th>Actions</th>
            </tr>
            <tr v-if="activeTab === 'students'">
              <th>Name</th><th>Email</th><th>CGPA</th><th>Actions</th>
            </tr>
            <tr v-if="activeTab === 'drives'">
              <th>Title</th><th>Company</th><th>Status</th><th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in items" :key="item.id">
              <template v-if="activeTab === 'companies'">
                <td>{{ item.name }}</td><td>{{ item.email }}</td>
                <td><span class="badge" :class="item.is_approved ? 'bg-success' : 'bg-warning'">{{ item.is_approved ? 'Approved' : 'Pending' }}</span></td>
                <td>
                  <button v-if="!item.is_approved" @click="action('companies', item.id, 'approve')" class="btn btn-sm btn-success me-2">Approve</button>
                  <button @click="action('companies', item.id, 'blacklist')" class="btn btn-sm" :class="item.is_blacklisted ? 'btn-secondary' : 'btn-danger'">
                    {{ item.is_blacklisted ? 'Un-Blacklist' : 'Blacklist' }}
                  </button>
                </td>
              </template>
              
              <template v-if="activeTab === 'students'">
                <td>{{ item.name }}</td><td>{{ item.email }}</td><td>{{ item.cgpa || 'N/A' }}</td>
                <td>
                  <button @click="action('students', item.id, 'blacklist')" class="btn btn-sm" :class="item.is_blacklisted ? 'btn-secondary' : 'btn-danger'">
                    {{ item.is_blacklisted ? 'Un-Blacklist' : 'Blacklist' }}
                  </button>
                </td>
              </template>

              <template v-if="activeTab === 'drives'">
                <td>{{ item.title }}</td><td>{{ item.company }}</td>
                <td><span class="badge" :class="item.status === 'Approved' ? 'bg-success' : 'bg-info'">{{ item.status }}</span></td>
                <td>
                  <button v-if="item.status === 'Pending'" @click="action('drives', item.id, 'approve')" class="btn btn-sm btn-success me-2">Approve</button>
                  <button v-if="item.status === 'Pending'" @click="action('drives', item.id, 'reject')" class="btn btn-sm btn-danger">Reject</button>
                </td>
              </template>
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
  data() { return { stats: {}, items: [], activeTab: 'companies' } },
  methods: {
    async fetchStats() {
      const res = await axios.get('http://localhost:5000/api/admin/stats')
      this.stats = res.data
    },
    async fetchData(tab) {
      this.activeTab = tab
      const res = await axios.get(`http://localhost:5000/api/admin/manage/${tab}`)
      this.items = res.data
    },
    async action(target, id, type) {
      await axios.post(`http://localhost:5000/api/admin/manage/${target}`, { id, action: type })
      this.fetchStats(); this.fetchData(this.activeTab)
    },
    logout() { localStorage.clear(); this.$router.push('/') }
  },
  mounted() { this.fetchStats(); this.fetchData('companies') }
}
</script>